#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.i18n import _
from logging import debug, warning, error
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish import domish
from twisted.internet import defer
from time import time
from wokkel import disco, iwokkel
from zope.interface import implements
import copy
try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

# Don't forget to set it to False before you commit
_DEBUG = False

PLUGIN_INFO = {
    "name": "Room game",
    "import_name": "ROOM-GAME",
    "type": "MISC",
    "protocols": [],
    "dependencies": ["XEP-0045", "XEP-0249"],
    "main": "RoomGame",
    "handler": "no",  # handler MUST be "no" (dynamic inheritance)
    "description": _("""Base class for MUC games""")
}


class RoomGame(object):
    """This class is used to help launching a MUC game.

    Bridge methods callbacks: prepareRoom, playerReady, createGame
    Triggered methods: userJoinedTrigger, userLeftTrigger
    Also called from subclasses: newRound

    For examples of messages sequences, please look in sub-classes.
    """

    # Values for self.invite_mode (who can invite after the game creation)
    FROM_ALL, FROM_NONE, FROM_REFEREE, FROM_PLAYERS = xrange(0, 4)
    # Values for self.wait_mode (for who we should wait before creating the game)
    FOR_ALL, FOR_NONE = xrange(0, 2)
    # Values for self.join_mode (who can join the game - NONE means solo game)
    ALL, INVITED, NONE = xrange(0, 3)
    # Values for ready_mode (how to turn a MUC user into a player)
    ASK, FORCE = xrange(0, 2)

    MESSAGE = '/message'
    REQUEST = '%s/%s[@xmlns="%s"]'

    def __init__(self, host):
        """For other plugin to dynamically inherit this class, it is necessary to not use __init__ but _init_.
        The subclass itself must be initialized this way:

        class MyGame(object):

            def inheritFromRoomGame(self, host):
                global RoomGame
                RoomGame = host.plugins["ROOM-GAME"].__class__
                self.__class__ = type(self.__class__.__name__, (self.__class__, RoomGame, object), {})

            def __init__(self, host):
                self.inheritFromRoomGame(host)
                RoomGame._init_(self, host, ...)

        """
        self.host = host

    def _init_(self, host, plugin_info, ns_tag, game_init=None, player_init=None):
        """
        @param host
        @param plugin_info: PLUGIN_INFO map of the game plugin
        @param ns_tag: couple (nameservice, tag) to construct the messages
        @param game_init: dictionary for general game initialization
        @param player_init: dictionary for player initialization, applicable to each player
        """
        self.host = host
        self.name = plugin_info["import_name"]
        self.ns_tag = ns_tag
        self.request = self.REQUEST % (self.MESSAGE, ns_tag[1], ns_tag[0])
        if game_init is None:
            game_init = {}
        if player_init is None:
            player_init = {}
        self.game_init = game_init
        self.player_init = player_init
        self.games = {}
        self.invitations = {}  # list of couple (x, y) with x the time and y a list of users

        # These are the default settings, which can be overwritten by child class after initialization
        self.invite_mode = self.FROM_PLAYERS if self.player_init == {} else self.FROM_NONE
        self.wait_mode = self.FOR_NONE if self.player_init == {} else self.FOR_ALL
        self.join_mode = self.INVITED
        self.ready_mode = self.FORCE  # TODO: asking for confirmation is not implemented

        # this has been added for testing purpose. It is sometimes needed to remove a dependence
        # while building the synchronization data, for example to replace a call to time.time()
        # by an arbitrary value. If needed, this attribute would be set to True from the testcase.
        self.testing = False

        host.trigger.add("MUC user joined", self.userJoinedTrigger)
        host.trigger.add("MUC user left", self.userLeftTrigger)

    def _createOrInvite(self, room, other_players, profile):
        """
        This is called only when someone explicitly wants to play.
        The game will not be created if one already exists in the room,
        also its creation could be postponed until all the expected players
        join the room (in that case it will be created from userJoinedTrigger).
        @param room: instance of wokkel.muc.Room
        @param other_players: list for other players JID userhosts
        """
        user_jid = self.host.getJidNStream(profile)[0]
        room_jid_s = room.occupantJID.userhost()
        nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid_s, profile)
        nicks = [nick]
        if self._gameExists(room_jid_s):
            if not self._checkJoinAuth(room_jid_s, user_jid.userhost(), nick):
                return
            nicks.extend(self._invitePlayers(room, other_players, nick, profile))
            self._updatePlayers(room_jid_s, nicks, True, profile)
        else:
            self._initGame(room_jid_s, nick)
            (auth, waiting, missing) = self._checkWaitAuth(room, other_players)
            nicks.extend(waiting)
            nicks.extend(self._invitePlayers(room, missing, nick, profile))
            if auth:
                self.createGame(room_jid_s, nicks, profile)
            else:
                self._updatePlayers(room_jid_s, nicks, False, profile)

    def _initGame(self, room_jid_s, referee_nick):
        """Important: do not add the referee to 'players' yet. For a
        <players /> message to be emitted whenever a new player is joining,
        it is necessary to not modify 'players' outside of _updatePlayers.
        """
        referee = room_jid_s + '/' + referee_nick
        self.games[room_jid_s] = {'referee': referee, 'players': [], 'started': False, 'status': {}}
        self.games[room_jid_s].update(copy.deepcopy(self.game_init))
        self.invitations.setdefault(room_jid_s, [])

    def _gameExists(self, room_jid_s, started=False):
        """Return True if a game has been initialized/started.
        @param started: if False, the game must be initialized to return True,
        otherwise it must be initialized and started with createGame.
        @return: True if a game is initialized/started in that room"""
        return room_jid_s in self.games and (not started or self.games[room_jid_s]['started'])

    def _checkJoinAuth(self, room_jid_s, user_jid_s=None, nick="", verbose=False):
        """Checks if this profile is allowed to join the game.
        The parameter nick is used to check if the user is already
        a player in that game. When this method is called from
        userJoinedTrigger, nick is also used to check the user
        identity instead of user_jid_s (see TODO comment below).
        @param room_jid_s: the room hosting the game
        @param user_jid_s: JID userhost of the user
        @param nick: nick of the user
        @return: True if this profile can join the game
        """
        auth = False
        if not self._gameExists(room_jid_s):
            auth = False
        elif self.join_mode == self.ALL or self.isPlayer(room_jid_s, nick):
            auth = True
        elif self.join_mode == self.INVITED:
            user_jid_s = JID(user_jid_s).userhost()
            # considering all the batches of invitations
            for invitations in self.invitations[room_jid_s]:
                if user_jid_s is not None:
                    if user_jid_s in invitations[1]:
                        auth = True
                        break
                else:
                    # TODO: that's not secure enough but what to do if
                    # wokkel.muc.User's 'entity' attribute is not set?!
                    if nick in [JID(invited).user for invited in invitations[1]]:
                        auth = True
                        break

        if not auth and (verbose or _DEBUG):
            debug(_("%(user)s not allowed to join the game %(game)s in %(room)s") % {'user': user_jid_s or nick, 'game': self.name, 'room': room_jid_s})
        return auth

    def _updatePlayers(self, room_jid_s, nicks, sync, profile):
        """Update the list of players and signal to the room that some players joined the game.
        If sync is True, the news players are synchronized with the game data they have missed.
        Remark: self.games[room_jid_s]['players'] should not be modified outside this method.
        @param room_jid_s: room userhost
        @param nicks: list of players nicks in the room (referee included, in first position)
        @param sync: set to True to send synchronization data to the new players
        @param profile
        """
        if nicks == []:
            return
        # this is better than set(nicks).difference(...) as it keeps the order
        new_nicks = [nick for nick in nicks if nick not in self.games[room_jid_s]['players']]
        if len(new_nicks) == 0:
            return

        def setStatus(status):
            for nick in new_nicks:
                self.games[room_jid_s]['status'][nick] = status

        sync = sync and self._gameExists(room_jid_s, True) and len(self.games[room_jid_s]['players']) > 0
        setStatus('desync' if sync else 'init')
        self.games[room_jid_s]['players'].extend(new_nicks)
        self._synchronizeRoom(room_jid_s, [JID(room_jid_s)], profile)
        if sync:
            setStatus('init')

    def _synchronizeRoom(self, room_jid_s, recipients, profile):
        """Communicate the list of players to the whole room or only to some users,
        also send the synchronization data to the players who recently joined the game.
        @param room_jid_s: room userhost
        @recipients: list of JIDs, the recipients of the message could be:
        - room JID
        - room JID + "/" + user nick
        @param profile
        """
        if self._gameExists(room_jid_s, started=True):
            element = self._createStartElement(self.games[room_jid_s]['players'])
        else:
            element = self._createStartElement(self.games[room_jid_s]['players'], name="players")
        elements = [(element, None, None)]

        sync_args = []
        sync_data = self._getSyncData(room_jid_s)
        for nick in sync_data:
            user_jid = JID(room_jid_s + '/' + nick)
            if user_jid in recipients:
                user_elements = copy.deepcopy(elements)
                for child in sync_data[nick]:
                    user_elements.append((child, None, None))
                recipients.remove(user_jid)
            else:
                user_elements = [(child, None, None) for child in sync_data[nick]]
            sync_args.append(([user_jid, user_elements], {'profile': profile}))

        for recipient in recipients:
            self._sendElements(recipient, elements, profile=profile)
        for args, kwargs in sync_args:
            self._sendElements(*args, **kwargs)

    def _getSyncData(self, room_jid_s, force_nicks=None):
        """The synchronization data are returned for each player who
        has the state 'desync' or if he's been contained by force_nicks.
        @param room_jid_s: room userhost
        @param force_nicks: force the synchronization for this list of the nicks
        @return: a mapping between player nicks and a list of elements to
        be sent by self._synchronizeRoom for the game to be synchronized.
        """
        if not self._gameExists(room_jid_s):
            return {}
        data = {}
        status = self.games[room_jid_s]['status']
        nicks = [nick for nick in status if status[nick] == 'desync']
        if force_nicks is None:
            force_nicks = []
        for nick in force_nicks:
            if nick not in nicks:
                nicks.append(nick)
        for nick in nicks:
            elements = self.getSyncDataForPlayer(room_jid_s, nick)
            if elements:
                data[nick] = elements
        return data

    def getSyncDataForPlayer(self, room_jid_s, nick):
        """This method may (and should probably) be overwritten by a child class.
        @param room_jid_s: room userhost
        @param nick: the nick of the player to be synchronized
        @return: a list of elements to synchronize this player with the game.
        """
        return []

    def _invitePlayers(self, room, other_players, nick, profile):
        """Invite players to a room, associated game may exist or not.
        @param room: wokkel.muc.Room instance
        @param other_players: list of JID userhosts to invite
        @param nick: nick of the user who send the invitation
        @return: list of room nicks for invited players who are already in the room
        """
        room_jid = room.occupantJID.userhostJID()
        room_jid_s = room.occupantJID.userhost()
        if not self._checkInviteAuth(room_jid_s, nick):
            return []
        # TODO: remove invitation waiting for too long, using the time data
        players_jids = [JID(player) for player in other_players]
        self.invitations[room_jid_s].append((time(), [player.userhost() for player in players_jids]))
        nicks = []
        for player_jid in [player.userhostJID() for player in players_jids]:
            # TODO: find a way to make it secure
            other_nick = self.host.plugins["XEP-0045"].getRoomNickOfUser(room, player_jid, secure=self.testing)
            if other_nick is None:
                self.host.plugins["XEP-0249"].invite(player_jid, room_jid, {"game": self.name}, profile)
            else:
                nicks.append(other_nick)
        return nicks

    def _checkInviteAuth(self, room_jid_s, nick, verbose=False):
        """Checks if this user is allowed to invite players
        @param room_jid_s: room userhost
        @param nick: user nick in the room
        @param verbose: display debug message
        @return: True if the user is allowed to invite other players
        """
        auth = False
        if self.invite_mode == self.FROM_ALL or not self._gameExists(room_jid_s):
            auth = True
        elif self.invite_mode == self.FROM_NONE:
            auth = not self._gameExists(room_jid_s, started=True) and self.isReferee(room_jid_s, nick)
        elif self.invite_mode == self.FROM_REFEREE:
            auth = self.isReferee(room_jid_s, nick)
        elif self.invite_mode == self.FROM_PLAYERS:
            auth = self.isPlayer(room_jid_s, nick)
        if not auth and (verbose or _DEBUG):
            debug(_("%(user)s not allowed to invite for the game %(game)s in %(room)s") % {'user': nick, 'game': self.name, 'room': room_jid_s})
        return auth

    def isReferee(self, room_jid_s, nick):
        """Checks if the player with this nick is the referee for the game in this room"
        @param room_jid_s: room userhost
        @param nick: user nick in the room
        @return: True if the user is the referee of the game in this room
        """
        if not self._gameExists(room_jid_s):
            return False
        return room_jid_s + '/' + nick == self.games[room_jid_s]['referee']

    def isPlayer(self, room_jid_s, nick):
        """Checks if the user with this nick is a player for the game in this room.
        @param room_jid_s: room userhost
        @param nick: user nick in the room
        @return: True if the user is a player of the game in this room
        """
        if not self._gameExists(room_jid_s):
            return False
        # Important: the referee is not in the 'players' list right after
        # the game initialization, that's why we do also check with isReferee
        return nick in self.games[room_jid_s]['players'] or self.isReferee(room_jid_s, nick)

    def _checkWaitAuth(self, room, other_players, verbose=False):
        """Check if we must wait for other players before starting the game.
        @param room: wokkel.muc.Room instance
        @param other_players: list of players JID userhosts without the referee
        @param verbose: display debug message
        @return: (x, y, z) with:
        x: False if we must wait, True otherwise
        y: the nicks of the players that have been checked and confirmed
        z: the players that have not been checked or that are missing
        """
        if self.wait_mode == self.FOR_NONE or other_players == []:
            result = (True, [], other_players)
        elif len(room.roster) < len(other_players):
            # do not check the players until we may actually have them all
            result = (False, [], other_players)
        else:
            # TODO: find a way to make it secure
            (nicks, missing) = self.host.plugins["XEP-0045"].getRoomNicksOfUsers(room, other_players, secure=False)
            result = (len(nicks) == len(other_players), nicks, missing)
        if not result[0] and (verbose or _DEBUG):
            debug(_("Still waiting for %(users)s before starting the game %(game)s in %(room)s") % {'users': result[2], 'game': self.name, 'room': room.occupantJID.userhost()})
        return result

    def getUniqueName(self, muc_service="", profile_key='@DEFAULT@'):
        """
        @param muc_service: you can leave empty to autofind the muc service
        @param profile_key
        @return: a unique name for a new room to be created
        """
        room = self.host.plugins["XEP-0045"].getUniqueName(muc_service, profile_key=profile_key)
        return "sat_%s_%s" % (self.name.lower(), room) if room != "" else ""

    def prepareRoom(self, other_players=None, room_jid_s=None, profile_key='@NONE@'):
        """Prepare the room for a game: create it if it doesn't exist and invite players.
        @param other_players: list for other players JID userhosts
        @param room_jid_s: JID userhost of the room, or None to generate a unique name
        @param profile_key
        """
        debug(_('Preparing room for %s game') % self.name)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("Unknown profile"))
            return
        if other_players is None:
            other_players = []

        def roomJoined(room):
            """@param room: instance of wokkel.muc.Room"""
            self._createOrInvite(room, [JID(player).userhost() for player in other_players], profile)

        def afterClientInit(room_jid_s):
            """Create/join the given room, or a unique generated one if no room is specified.
            @param room_jids: userhost of the room to join
            """
            if room_jid_s is not None and room_jid_s != "":  # a room name has been specified
                if room_jid_s in self.host.plugins["XEP-0045"].clients[profile].joined_rooms:
                    roomJoined(self.host.plugins["XEP-0045"].clients[profile].joined_rooms[room_jid_s])
                    return
            else:
                room_jid_s = self.getUniqueName(profile_key=profile_key)
                if room_jid_s == "":
                    return
            user_jid = self.host.getJidNStream(profile)[0]
            d = self.host.plugins["XEP-0045"].join(JID(room_jid_s), user_jid.user, {}, profile)
            d.addCallback(roomJoined)

        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            return
        client.client_initialized.addCallback(lambda ignore: afterClientInit(room_jid_s))

    def userJoinedTrigger(self, room, user, profile):
        """This trigger is used to check if the new user can take part of a game,
        create the game if we were waiting for him or just update the players list.
        @room: wokkel.muc.Room object. room.roster is a dict{wokkel.muc.User.nick: wokkel.muc.User}
        @user: wokkel.muc.User object. user.nick is a unicode and user.entity a JID
        @return: True to not interrupt the main process.
        """
        room_jid_s = room.occupantJID.userhost()
        profile_nick = room.occupantJID.resource
        if not self.isReferee(room_jid_s, profile_nick):
            return True  # profile is not the referee
        if not self._checkJoinAuth(room_jid_s, user.entity.userhost() if user.entity else None, user.nick):
            # user not allowed but let him know that we are playing :p
            self._synchronizeRoom(room_jid_s, [JID(room_jid_s + '/' + user.nick)], profile)
            return True
        if self.wait_mode == self.FOR_ALL:
            # considering the last batch of invitations
            batch = len(self.invitations[room_jid_s]) - 1
            if batch < 0:
                error("Invitations from %s to play %s in %s have been lost!" % (profile_nick, self.name, room_jid_s))
                return True
            other_players = self.invitations[room_jid_s][batch][1]
            (auth, nicks, dummy) = self._checkWaitAuth(room, other_players)
            if auth:
                del self.invitations[room_jid_s][batch]
                nicks.insert(0, profile_nick)  # add the referee
                self.createGame(room_jid_s, nicks, profile_key=profile)
                return True
        # let the room know that a new player joined
        self._updatePlayers(room_jid_s, [user.nick], True, profile)
        return True

    def userLeftTrigger(self, room, user, profile):
        """This trigger is used to update or stop the game when a user leaves.
        @room: wokkel.muc.Room object. room.roster is a dict{wokkel.muc.User.nick: wokkel.muc.User}
        @user: wokkel.muc.User object. user.nick is a unicode and user.entity a JID
        @return: True to not interrupt the main process.
        """
        room_jid_s = room.occupantJID.userhost()
        profile_nick = room.occupantJID.resource
        if not self.isReferee(room_jid_s, profile_nick):
            return True  # profile is not the referee
        if self.isPlayer(room_jid_s, user.nick):
            try:
                self.games[room_jid_s]['players'].remove(user.nick)
            except ValueError:
                pass
            if len(self.games[room_jid_s]['players']) == 0:
                del self.games[room_jid_s]  # finish the game
                return True
            if self.wait_mode == self.FOR_ALL:
                # allow this user to join the game again
                user_jid_s = user.entity.userhost()
                if len(self.invitations[room_jid_s]) == 0:
                    self.invitations[room_jid_s].append((time(), [user_jid_s]))
                else:
                    batch = 0  # add to the first batch of invitations
                    if user_jid_s not in self.invitations[room_jid_s][batch][1]:
                        self.invitations[room_jid_s][batch][1].append(user_jid_s)
        return True

    def _checkCreateGameAndInit(self, room_jid_s, profile):
        """Check if that profile can create the game. If the game can be created
        but is not initialized yet, this method will also do the initialization.
        @param room_jid_s: room userhost
        @param profile
        @return: a couple (create, sync) with:
        - create: set to True to allow the game creation
        - sync: set to True to advice a game synchronization
        """
        user_nick = self.host.plugins["XEP-0045"].getRoomNick(room_jid_s, profile)
        if not user_nick:
            error('Internal error: profile %s has not joined the room %s' % (profile, room_jid_s))
            return False, False
        if self._gameExists(room_jid_s):
            is_referee = self.isReferee(room_jid_s, user_nick)
            if self._gameExists(room_jid_s, started=True):
                warning(_("%(game)s game already created in room %(room)s") % {'game': self.name, 'room': room_jid_s})
                return False, is_referee
            elif not is_referee:
                warning(_("%(game)s game in room %(room)s can only be created by %(user)s") % {'game': self.name, 'room': room_jid_s, 'user': user_nick})
                return False, False
        else:
            self._initGame(room_jid_s, user_nick)
        return True, False

    def createGame(self, room_jid_s, nicks=None, profile_key='@NONE@'):
        """Create a new game - this can be called directly from a frontend
        and skips all the checks and invitation system, but the game must
        not exist and all the players must be in the room already.
        @param room_jid: JID userhost of the room
        @param nicks: list of players nicks in the room (referee included, in first position)
        @param profile_key: %(doc_profile_key)s"""
        debug(_("Creating %(game)s game in room %(room)s") % {'game': self.name, 'room': room_jid_s})
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("profile %s is unknown") % profile_key)
            return
        (create, sync) = self._checkCreateGameAndInit(room_jid_s, profile)
        if nicks is None:
            nicks = []
        if not create:
            if sync:
                self._updatePlayers(room_jid_s, nicks, True, profile)
            return
        self.games[room_jid_s]['started'] = True
        self._updatePlayers(room_jid_s, nicks, False, profile)
        if self.player_init:
            # specific data to each player (score, private data)
            self.games[room_jid_s].setdefault('players_data', {})
            for nick in nicks:
                # The dict must be COPIED otherwise it is shared between all users
                self.games[room_jid_s]['players_data'][nick] = copy.deepcopy(self.player_init)

    def playerReady(self, player, referee, profile_key='@NONE@'):
        """Must be called when player is ready to start a new game
        @param player: the player nick in the room
        @param referee: referee userhost
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            error(_("profile %s is unknown") % profile_key)
            return
        debug('new player ready: %s' % profile)
        # TODO: we probably need to add the game and room names in the sent message
        self.send(JID(referee), 'player_ready', {'player': player}, profile=profile)

    def newRound(self, room_jid, data, profile):
        """Launch a new round (reinit the user data)
        @param room_jid: room userhost
        @param data: a couple (common_data, msg_elts) with:
        - common_data: backend initialization data for the new round
        - msg_elts: dict to map each user to his specific initialization message
        @param profile
        """
        debug(_('new round for %s game') % self.name)
        game_data = self.games[room_jid.userhost()]
        players = game_data['players']
        players_data = game_data['players_data']
        game_data['stage'] = "init"

        common_data, msg_elts = copy.deepcopy(data) if data is not None else (None, None)

        if isinstance(msg_elts, dict):
            for player in players:
                to_jid = JID(room_jid.userhost() + "/" + player)  # FIXME: gof:
                elem = msg_elts[player] if isinstance(msg_elts[player], domish.Element) else None
                self.send(to_jid, elem, profile=profile)
        elif isinstance(msg_elts, domish.Element):
            self.send(room_jid, msg_elts, profile=profile)
        if common_data is not None:
            for player in players:
                players_data[player].update(copy.deepcopy(common_data))

    def _createGameElt(self, to_jid):
        """Create a generic domish Element for the game messages
        @param to_jid: JID of the recipient
        @return: the created element
        """
        type_ = "normal" if to_jid.resource else "groupchat"
        elt = domish.Element((None, 'message'))
        elt["to"] = to_jid.full()
        elt["type"] = type_
        elt.addElement(self.ns_tag)
        return elt

    def _createStartElement(self, players=None, name="started"):
        """Create a domish Element listing the game users
        @param players: list of the players
        @param name: element name:
        - "started" to signal the players that the game has been started
        - "players" to signal the list of players when the game is not started yet
        @return the create element
        """
        started_elt = domish.Element((None, name))
        if players is None:
            return started_elt
        idx = 0
        for player in players:
            player_elt = domish.Element((None, 'player'))
            player_elt.addContent(player)
            player_elt['index'] = str(idx)
            idx += 1
            started_elt.addChild(player_elt)
        return started_elt

    def _sendElements(self, to_jid, data, profile=None):
        """
        @param to_jid: recipient JID
        @param data: list of (elem, attr, content) with:
        - elem: domish.Element, unicode or a couple:
                - domish.Element to be directly added as a child to the message
                - unicode name or couple (uri, name) to create a new domish.Element
                  and add it as a child to the message (see domish.Element.addElement)
        - attrs: dictionary of attributes for the new child
        - content: unicode that is appended to the child content
        @param profile: the profile from which the message is sent
        @return: a Deferred instance
        """
        if profile is None:
            error(_("Message can not be sent without a sender profile"))
            return defer.fail(None)
        msg = self._createGameElt(to_jid)
        for elem, attrs, content in data:
            if elem is not None:
                if isinstance(elem, domish.Element):
                    msg.firstChildElement().addChild(elem)
                else:
                    elem = msg.firstChildElement().addElement(elem)
                if attrs is not None:
                    elem.attributes.update(attrs)
                if content is not None:
                    elem.addContent(content)
        self.host.profiles[profile].xmlstream.send(msg)
        return defer.succeed(None)

    def send(self, to_jid, elem=None, attrs=None, content=None, profile=None):
        """
        @param to_jid: recipient JID
        @param elem: domish.Element, unicode or a couple:
        - domish.Element to be directly added as a child to the message
        - unicode name or couple (uri, name) to create a new domish.Element
          and add it as a child to the message (see domish.Element.addElement)
        @param attrs: dictionary of attributes for the new child
        @param content: unicode that is appended to the child content
        @param profile: the profile from which the message is sent
        @return: a Deferred instance
        """
        return self._sendElements(to_jid, [(elem, attrs, content)], profile)

    def getHandler(self, profile):
        return RoomGameHandler(self)


class RoomGameHandler (XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(self.plugin_parent.request, self.plugin_parent.room_game_cmd, profile=self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(self.plugin_parent.ns_tag[0])]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
