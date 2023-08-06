#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013, 2014 Adrien Cossa (souliane@mailoo.org)

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

""" Helpers class for plugin dependencies """

from constants import Const
from sat.plugins import plugin_xep_0045
from twisted.internet import defer
from wokkel.muc import Room, User


class FakeMUCClient(object):
    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.joined_rooms = {}

    def join(self, roomJID, nick, profile):
        """
        @param roomJID: the room JID
        @param nick: nick to be used in the room
        @param profile: the profile of the user joining the room
        @return: the deferred joined wokkel.muc.Room instance
        """
        roster = {}

        # ask the other profiles to fill our roster
        for i in xrange(0, len(Const.PROFILE)):
            other_profile = Const.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[roomJID.userhost()]
                roster.setdefault(other_room.nick, User(other_room.nick, Const.PROFILE_DICT[other_profile]))
                for other_nick in other_room.roster:
                    roster.setdefault(other_nick, other_room.roster[other_nick])
            except (AttributeError, KeyError):
                pass

        # rename our nick if it already exists
        while nick in roster.keys():
            if Const.PROFILE_DICT[profile].userhost() == roster[nick].entity.userhost():
                break  # same user with different resource --> same nickname
            nick = nick + "_"

        room = Room(roomJID, nick)
        room.roster = roster
        self.joined_rooms[roomJID.userhost()] = room

        # fill the other rosters with the new entry
        for i in xrange(0, len(Const.PROFILE)):
            other_profile = Const.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[roomJID.userhost()]
                other_room.roster.setdefault(room.nick, User(room.nick, Const.PROFILE_DICT[profile]))
            except (AttributeError, KeyError):
                pass

        return defer.succeed(room)

    def leave(self, roomJID, profile):
        """
        @param roomJID: the room JID
        @param profile: the profile of the user joining the room
        @return: a dummy deferred
        """
        room = self.joined_rooms[roomJID.userhost()]
        # remove ourself from the other rosters
        for i in xrange(0, len(Const.PROFILE)):
            other_profile = Const.PROFILE[i]
            if other_profile == profile:
                continue
            try:
                other_room = self.plugin_parent.clients[other_profile].joined_rooms[roomJID.userhost()]
                del other_room.roster[room.nick]
            except (AttributeError, KeyError):
                pass
        del self.joined_rooms[roomJID.userhost()]
        return defer.Deferred()


class FakeXEP_0045(plugin_xep_0045.XEP_0045):

    def __init__(self, host):
        self.host = host
        self.clients = {}
        for profile in Const.PROFILE:
            self.clients[profile] = FakeMUCClient(self)

    def join(self, room_jid, nick, options={}, profile_key='@DEFAULT@'):
        """
        @param roomJID: the room JID
        @param nick: nick to be used in the room
        @param options: ignore
        @param profile_key: the profile of the user joining the room
        @return: the deferred joined wokkel.muc.Room instance or None
        """
        profile = self.host.memory.getProfileName(profile_key)
        room_jid_s = room_jid.userhost()
        if room_jid_s in self.clients[profile].joined_rooms:
            return defer.succeed(None)
        room = self.clients[profile].join(room_jid, nick, profile)
        return room

    def joinRoom(self, muc_index, user_index):
        """Called by tests
        @return: the nickname of the user who joined room"""
        muc_jid = Const.MUC[muc_index]
        nick = Const.JID[user_index].user
        profile = Const.PROFILE[user_index]
        self.join(muc_jid, nick, profile_key=profile)
        return self.getNick(muc_index, user_index)

    def leave(self, room_jid, profile_key='@DEFAULT@'):
        """
        @param roomJID: the room JID
        @param profile_key: the profile of the user leaving the room
        @return: a dummy deferred
        """
        profile = self.host.memory.getProfileName(profile_key)
        room_jid_s = room_jid.userhost()
        if room_jid_s not in self.clients[profile].joined_rooms:
            raise plugin_xep_0045.UnknownRoom("This room has not been joined")
        return self.clients[profile].leave(room_jid, profile)

    def leaveRoom(self, muc_index, user_index):
        """Called by tests
        @return: the nickname of the user who left the room"""
        muc_jid = Const.MUC[muc_index]
        nick = self.getNick(muc_index, user_index)
        profile = Const.PROFILE[user_index]
        self.leave(muc_jid, profile_key=profile)
        return nick

    def getRoom(self, muc_index, user_index):
        """Called by tests
        @return: a wokkel.muc.Room instance"""
        profile = Const.PROFILE[user_index]
        muc_s = Const.MUC_STR[muc_index]
        try:
            return self.clients[profile].joined_rooms[muc_s]
        except (AttributeError, KeyError):
            return None

    def getNick(self, muc_index, user_index):
        try:
            return self.getRoomNick(Const.MUC_STR[muc_index], Const.PROFILE[user_index])
        except (KeyError, AttributeError):
            return ''

    def getNickOfUser(self, muc_index, user_index, profile_index, secure=True):
        try:
            room = self.clients[Const.PROFILE[profile_index]].joined_rooms[Const.MUC_STR[muc_index]]
            return self.getRoomNickOfUser(room, Const.JID_STR[user_index])
        except (KeyError, AttributeError):
            return None


class FakeXEP_0249(object):

    def __init__(self, host):
        self.host = host

    def invite(self, target, room, options={}, profile_key='@DEFAULT@'):
        """
        Invite a user to a room. To accept the invitation from a test,
        just call FakeXEP_0045.joinRoom (no need to have a dedicated method).
        @param target: jid of the user to invite
        @param room: jid of the room where the user is invited
        @options: attribute with extra info (reason, password) as in #XEP-0249
        @profile_key: %(doc_profile_key)s
        """
        pass
