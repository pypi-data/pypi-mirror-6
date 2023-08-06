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

from sat.core.i18n import _, languageSwitch
from twisted.application import service
from twisted.internet import defer

from twisted.words.protocols.jabber import jid, xmlstream
from twisted.words.xish import domish

from twisted.internet import reactor

from wokkel import compat
from wokkel.xmppim import RosterItem

from sat.bridge.DBus import DBusBridge
import logging
from logging import debug, info, warning, error

import sys
import os.path

from sat.core.default_config import CONST
from sat.core import xmpp
from sat.core import exceptions
from sat.memory.memory import Memory, NO_SECURITY_LIMIT
from sat.tools.xml_tools import tupleList2dataForm
from sat.tools.misc import TriggerManager
from glob import glob
from uuid import uuid4

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

### logging configuration FIXME: put this elsewhere ###
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s')
###

sat_id = 0


def sat_next_id():
    global sat_id
    sat_id += 1
    return "sat_id_" + str(sat_id)


class MessageSentAndStored(Exception):
    """ Exception to raise if the message has been already sent and stored in the
    history by the trigger, so the rest of the process should be stopped. This
    should normally be raised by the trigger with the minimal priority """
    def __init__(self, reason, mess_data):
        Exception(reason)
        self.mess_data = mess_data  # added for testing purpose


class AbortSendMessage(Exception):
    """ Exception to raise if sending the message should be aborted. This can be
    raised by any trigger but a side action should be planned by the trigger
    to inform the user about what happened """
    pass


class SAT(service.Service):

    @property
    def __version__(self):
        return self.getConst('client_version')

    def get_next_id(self):
        return sat_next_id()

    def getConst(self, name):
        """Return a constant"""
        try:
            _const = os.environ['SAT_CONST_%s' % name]
            if _const:
                warning(_("Constant %(name)s overrided with [%(value)s]") % {'name': name, 'value': _const})
                return _const
        except KeyError:
            pass
        if name not in CONST:
            error(_('Trying to access an undefined constant'))
            raise Exception
        return CONST[name]

    def setConst(self, name, value):
        """Save a constant"""
        if name in CONST:
            error(_('Trying to redefine a constant'))
            raise Exception
        CONST[name] = value

    def __init__(self):
        self._cb_map = {}  # map from callback_id to callbacks
        self._menus = {}  # dynamic menus. key: callback_id, value: menu data (dictionnary)
        self.__private_data = {}  # used for internal callbacks (key = id) FIXME: to be removed
        self.profiles = {}
        self.plugins = {}

        self.memory = Memory(self)

        local_dir = self.memory.getConfig('', 'local_dir')
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        self.trigger = TriggerManager()  # trigger are used to change SàT behaviour

        try:
            self.bridge = DBusBridge()
        except exceptions.BridgeInitError:
            print (u"Bridge can't be initialised, can't start SàT core") # reactor is not launched yet, so we can't use error log
            sys.exit(1)
        self.bridge.register("getVersion", lambda: self.getConst('client_version'))
        self.bridge.register("getProfileName", self.memory.getProfileName)
        self.bridge.register("getProfilesList", self.memory.getProfilesList)
        self.bridge.register("getEntityData", lambda _jid, keys, profile: self.memory.getEntityData(jid.JID(_jid), keys, profile))
        self.bridge.register("createProfile", self.memory.createProfile)
        self.bridge.register("asyncCreateProfile", self.memory.asyncCreateProfile)
        self.bridge.register("deleteProfile", self.memory.deleteProfile)
        self.bridge.register("registerNewAccount", self.registerNewAccount)
        self.bridge.register("connect", self.connect)
        self.bridge.register("asyncConnect", self.asyncConnect)
        self.bridge.register("disconnect", self.disconnect)
        self.bridge.register("getContacts", self.getContacts)
        self.bridge.register("getContactsFromGroup", self.getContactsFromGroup)
        self.bridge.register("getLastResource", self.memory.getLastResource)
        self.bridge.register("getPresenceStatus", self.memory.getPresenceStatus)
        self.bridge.register("getWaitingSub", self.memory.getWaitingSub)
        self.bridge.register("getWaitingConf", self.getWaitingConf)
        self.bridge.register("sendMessage", self._sendMessage)
        self.bridge.register("getConfig", self.memory.getConfig)
        self.bridge.register("setParam", self.setParam)
        self.bridge.register("getParamA", self.memory.getStringParamA)
        self.bridge.register("asyncGetParamA", self.memory.asyncGetStringParamA)
        self.bridge.register("getParamsUI", self.memory.getParamsUI)
        self.bridge.register("getParams", self.memory.getParams)
        self.bridge.register("getParamsForCategory", self.memory.getParamsForCategory)
        self.bridge.register("getParamsCategories", self.memory.getParamsCategories)
        self.bridge.register("paramsRegisterApp", self.memory.paramsRegisterApp)
        self.bridge.register("getHistory", self.memory.getHistory)
        self.bridge.register("setPresence", self._setPresence)
        self.bridge.register("subscription", self.subscription)
        self.bridge.register("addContact", self._addContact)
        self.bridge.register("updateContact", self._updateContact)
        self.bridge.register("delContact", self._delContact)
        self.bridge.register("isConnected", self.isConnected)
        self.bridge.register("launchAction", self.launchCallback)
        self.bridge.register("confirmationAnswer", self.confirmationAnswer)
        self.bridge.register("getProgress", self.getProgress)
        self.bridge.register("getMenus", self.getMenus)
        self.bridge.register("getMenuHelp", self.getMenuHelp)

        self.memory.initialized.addCallback(self._postMemoryInit)

    def _postMemoryInit(self, ignore):
        """Method called after memory initialization is done"""
        info(_("Memory initialised"))
        self._import_plugins()

    def _import_plugins(self):
        """Import all plugins found in plugins directory"""
        import sat.plugins
        plugins_path = os.path.dirname(sat.plugins.__file__)
        plug_lst = [os.path.splitext(plugin)[0] for plugin in map(os.path.basename, glob(os.path.join(plugins_path, "plugin*.py")))]
        __plugins_to_import = {}  # plugins we still have to import
        for plug in plug_lst:
            plugin_path = 'sat.plugins.' + plug
            __import__(plugin_path)
            mod = sys.modules[plugin_path]
            plugin_info = mod.PLUGIN_INFO
            __plugins_to_import[plugin_info['import_name']] = (plugin_path, mod, plugin_info)
        while True:
            self._import_plugins_from_dict(__plugins_to_import)
            if not __plugins_to_import:
                break

    def _import_plugins_from_dict(self, plugins_to_import, import_name=None):
        """Recursively import and their dependencies in the right order
        @param plugins_to_import: dict where key=import_name and values= (plugin_path, module, plugin_info)"""
        if import_name in self.plugins:
            debug('Plugin [%s] already imported, passing' % import_name)
            return
        if not import_name:
            import_name, (plugin_path, mod, plugin_info) = plugins_to_import.popitem()
        else:
            if not import_name in plugins_to_import:
                raise ImportError(_('Dependency plugin not found: [%s]') % import_name)
            plugin_path, mod, plugin_info = plugins_to_import.pop(import_name)
        dependencies = plugin_info.setdefault("dependencies", [])
        for dependency in dependencies:
            if dependency not in self.plugins:
                debug('Recursively import dependency of [%s]: [%s]' % (import_name, dependency))
                self._import_plugins_from_dict(plugins_to_import, dependency)
        info(_("importing plugin: %s"), plugin_info['name'])
        self.plugins[import_name] = getattr(mod, plugin_info['main'])(self)
        if 'handler' in plugin_info and plugin_info['handler'] == 'yes':
            self.plugins[import_name].is_handler = True
        else:
            self.plugins[import_name].is_handler = False
        #TODO: test xmppclient presence and register handler parent

    def connect(self, profile_key='@NONE@'):
        """Connect to jabber server"""
        self.asyncConnect(profile_key)

    def asyncConnect(self, profile_key='@NONE@'):
        """Connect to jabber server with asynchronous reply
        @param profile_key: %(doc_profile)s
        """

        profile = self.memory.getProfileName(profile_key)
        if not profile:
            error(_('Trying to connect a non-exsitant profile'))
            raise exceptions.ProfileUnknownError(profile_key)

        if self.isConnected(profile):
            info(_("already connected !"))
            return defer.succeed("None")

        if profile in self.profiles:
            # avoid the following error when self.connect() is called twice for the same profile within a short time period:
            #   Jumping into debugger for post-mortem of exception ''SatXMPPClient' object has no attribute 'discoHandler'':
            #   > /usr/local/lib/python2.7/dist-packages/sat/plugins/plugin_xep_0115.py(151)generateHash()
            #   -> services = client.discoHandler.info(client.jid, client.jid, '').addCallback(generateHash_2, profile)
            # This is a strange issue that is often happening on my system since libervia is being run as a twisted plugin.
            # FIXME: properly find the problem an fix it
            debug("being connected...")
            return defer.succeed("None")

        def afterMemoryInit(ignore):
            """This part must be called when we have loaded individual parameters from memory"""
            try:
                port = int(self.memory.getParamA("Port", "Connection", profile_key=profile))
            except ValueError:
                error(_("Can't parse port value, using default value"))
                port = 5222
            current = self.profiles[profile] = xmpp.SatXMPPClient(
                self, profile,
                jid.JID(self.memory.getParamA("JabberID", "Connection", profile_key=profile), profile),
                self.memory.getParamA("Password", "Connection", profile_key=profile),
                self.memory.getParamA("Server", "Connection", profile_key=profile),
                port)

            current.messageProt = xmpp.SatMessageProtocol(self)
            current.messageProt.setHandlerParent(current)

            current.roster = xmpp.SatRosterProtocol(self)
            current.roster.setHandlerParent(current)

            current.presence = xmpp.SatPresenceProtocol(self)
            current.presence.setHandlerParent(current)

            current.fallBack = xmpp.SatFallbackHandler(self)
            current.fallBack.setHandlerParent(current)

            current.versionHandler = xmpp.SatVersionHandler(self.getConst('client_name'),
                                                            self.getConst('client_version'))
            current.versionHandler.setHandlerParent(current)

            current.identityHandler = xmpp.SatIdentityHandler()
            current.identityHandler.setHandlerParent(current)

            debug(_("setting plugins parents"))

            for plugin in self.plugins.iteritems():
                if plugin[1].is_handler:
                    plugin[1].getHandler(profile).setHandlerParent(current)
                connected_cb = getattr(plugin[1], "profileConnected", None)
                if connected_cb:
                    connected_cb(profile)

            current.startService()

            d = current.getConnectionDeferred()
            d.addCallback(lambda x: current.roster.got_roster)  # we want to be sure that we got the roster
            return d

        self.memory.startProfileSession(profile)
        return self.memory.loadIndividualParams(profile).addCallback(afterMemoryInit)

    def disconnect(self, profile_key):
        """disconnect from jabber server"""
        if not self.isConnected(profile_key):
            info(_("not connected !"))
            return
        profile = self.memory.getProfileName(profile_key)
        info(_("Disconnecting..."))
        self.profiles[profile].stopService()
        for plugin in self.plugins.iteritems():
            disconnected_cb = getattr(plugin[1], "profileDisconnected", None)
            if disconnected_cb:
                disconnected_cb(profile)

    def getContacts(self, profile_key):
        client = self.getClient(profile_key)
        if not client:
            raise exceptions.ProfileUnknownError(_('Asking contacts for a non-existant profile'))
        ret = []
        for item in client.roster.getItems():  # we get all items for client's roster
            # and convert them to expected format
            attr = client.roster.getAttributes(item)
            ret.append([item.jid.userhost(), attr, item.groups])
        return ret

    def getContactsFromGroup(self, group, profile_key):
        client = self.getClient(profile_key)
        if not client:
            raise exceptions.ProfileUnknownError(_("Asking group's contacts for a non-existant profile"))
        return [jid.full() for jid in client.roster.getJidsFromGroup(group)]

    def purgeClient(self, profile):
        """Remove reference to a profile client and purge cache
        the garbage collector can then free the memory"""
        try:
            del self.profiles[profile]
        except KeyError:
            error(_("Trying to remove reference to a client not referenced"))
        self.memory.purgeProfileSession(profile)

    def startService(self):
        info("Salut à toi ô mon frère !")
        #TODO: manage autoconnect
        #self.connect()

    def stopService(self):
        info("Salut aussi à Rantanplan")

    def run(self):
        debug(_("running app"))
        reactor.run()

    def stop(self):
        debug(_("stopping app"))
        reactor.stop()

    ## Misc methods ##

    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        profile = self.memory.getProfileName(profile_key)
        if not profile or not self.profiles[profile].isConnected():
            return (None, None)
        return (self.profiles[profile].jid, self.profiles[profile].xmlstream)

    def getClient(self, profile_key):
        """Convenient method to get client from profile key
        @return: client or None if it doesn't exist"""
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            return None
        return self.profiles[profile]

    def getClients(self, profile_key):
        """Convenient method to get list of clients from profile key (manage list through profile_key like @ALL@)
        @param profile_key: %(doc_profile_key)s
        @return: list of clients"""
        profile = self.memory.getProfileName(profile_key, True)
        if not profile:
            return []
        if profile == "@ALL@":
            return self.profiles.values()
        if profile.count('@') > 1:
            raise exceptions.ProfileKeyUnknownError
        return [self.profiles[profile]]

    def getClientHostJid(self, profile_key):
        """Convenient method to get the client host from profile key
        @return: host jid or None if it doesn't exist"""
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            return None
        return self.profiles[profile].getHostJid()

    def registerNewAccount(self, login, password, email, server, port=5222, id_=None, profile_key='@NONE@'):
        """Connect to a server and create a new account using in-band registration"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)

        next_id = id_ or self.get_next_id()  # the id is used to send server's answer
        serverRegistrer = xmlstream.XmlStreamFactory(xmpp.RegisteringAuthenticator(self, server, login, password, email, next_id, profile))
        connector = reactor.connectTCP(server, port, serverRegistrer)
        serverRegistrer.clientConnectionLost = lambda conn, reason: connector.disconnect()

        return next_id

    def registerNewAccountCB(self, data, profile):
        # FIXME: to be removed/redone elsewhere
        user = jid.parse(self.memory.getParamA("JabberID", "Connection", profile_key=profile))[0]
        password = self.memory.getParamA("Password", "Connection", profile_key=profile)
        server = self.memory.getParamA("Server", "Connection", profile_key=profile)

        if not user or not password or not server:
            raise exceptions.DataError(_("No user, password or server given, can't register new account."))

        # FIXME: to be fixed with XMLUI dialogs once their implemented
        confirm_id = sat_next_id()
        self.__private_data[confirm_id] = (id, profile)

        self.askConfirmation(
            confirm_id, "YES/NO",
            {"message": _("Are you sure to register new account [%(user)s] to server %(server)s ?") % {'user': user, 'server': server, 'profile': profile}},
            self.regisConfirmCB, profile)
        print "===============+++++++++++ REGISTER NEW ACCOUNT++++++++++++++============"

    def regisConfirmCB(self, id, accepted, data, profile):
        print _("register Confirmation CB ! (%s)") % str(accepted)
        action_id, profile = self.__private_data[id]
        del self.__private_data[id]
        if accepted:
            user = jid.parse(self.memory.getParamA("JabberID", "Connection", profile_key=profile))[0]
            password = self.memory.getParamA("Password", "Connection", profile_key=profile)
            server = self.memory.getParamA("Server", "Connection", profile_key=profile)
            self.registerNewAccount(user, password, None, server, id=action_id)
        else:
            self.actionResult(action_id, "SUPPRESS", {}, profile)

    ## Client management ##

    def setParam(self, name, value, category, security_limit, profile_key):
        """set wanted paramater and notice observers"""
        info(_("setting param: %(name)s=%(value)s in category %(category)s") % {'name': name, 'value': value, 'category': category})
        self.memory.setParam(name, value, category, security_limit, profile_key)

    def isConnected(self, profile_key):
        """Return connection status of profile
        @param profile_key: key_word or profile name to determine profile name
        @return True if connected
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            error(_('asking connection status for a non-existant profile'))
            return
        if profile not in self.profiles:
            return False
        return self.profiles[profile].isConnected()


    ## jabber methods ##

    def getWaitingConf(self, profile_key=None):
        assert(profile_key)
        client = self.getClient(profile_key)
        if not client:
            raise exceptions.ProfileNotInCacheError
        ret = []
        for conf_id in client._waiting_conf:
            conf_type, data = client._waiting_conf[conf_id][:2]
            ret.append((conf_id, conf_type, data))
        return ret

    def _sendMessage(self, to_s, msg, subject=None, mess_type='auto', extra={}, profile_key='@NONE@'):
        to_jid = jid.JID(to_s)
        #XXX: we need to use the dictionary comprehension because D-Bus return its own types, and pickle can't manage them. TODO: Need to find a better way
        return self.sendMessage(to_jid, msg, subject, mess_type, {unicode(key): unicode(value) for key, value in extra.items()}, profile_key=profile_key)

    def sendMessage(self, to_jid, msg, subject=None, mess_type='auto', extra={}, no_trigger=False, profile_key='@NONE@'):
        #FIXME: check validity of recipient
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        client = self.profiles[profile]
        current_jid = client.jid
        if extra is None:
            extra = {}
        mess_data = {  # we put data in a dict, so trigger methods can change them
            "to": to_jid,
            "message": msg,
            "subject": subject,
            "type": mess_type,
            "extra": extra,
        }
        treatments = defer.Deferred() # XXX: plugin can add their treatments to this deferred

        if mess_data["type"] == "auto":
            # we try to guess the type
            if mess_data["subject"]:
                mess_data["type"] = 'normal'
            elif not mess_data["to"].resource:  # if to JID has a resource, the type is not 'groupchat'
                # we may have a groupchat message, we check if the we know this jid
                try:
                    entity_type = self.memory.getEntityData(mess_data["to"], ['type'], profile)["type"]
                    #FIXME: should entity_type manage ressources ?
                except (exceptions.UnknownEntityError, KeyError):
                    entity_type = "contact"

                if entity_type == "chatroom":
                    mess_data["type"] = 'groupchat'
                else:
                    mess_data["type"] = 'chat'
            else:
                mess_data["type"] == 'chat'
            mess_data["type"] == "chat" if mess_data["subject"] else "normal"

        if not no_trigger:
            if not self.trigger.point("sendMessage", mess_data, treatments, profile):
                return defer.succeed(None)

        debug(_("Sending jabber message of type [%(type)s] to %(to)s...") % {"type": mess_data["type"], "to": to_jid.full()})
        mess_data['xml'] = domish.Element((None, 'message'))
        mess_data['xml']["to"] = mess_data["to"].full()
        mess_data['xml']["from"] = current_jid.full()
        mess_data['xml']["type"] = mess_data["type"]
        if mess_data["subject"]:
            mess_data['xml'].addElement("subject", None, subject)
        # message without body are used to send chat states
        if mess_data["message"]:
            mess_data['xml'].addElement("body", None, mess_data["message"])

        def sendErrback(e):
            text = '%s: %s' % (e.value.__class__.__name__, e.getErrorMessage())
            if e.check(MessageSentAndStored):
                debug(text)
            elif e.check(AbortSendMessage):
                warning(text)
                return e
            else:
                error("Unmanaged exception: %s" % text)
                return e

        treatments.addCallbacks(self.sendAndStoreMessage, sendErrback, [False, profile])
        treatments.callback(mess_data)
        return treatments

    def sendAndStoreMessage(self, mess_data, skip_send=False, profile=None):
        """Actually send and store the message to history, after all the treatments
        have been done. This has been moved outside the main sendMessage method
        because it is used by XEP-0033 to complete a server-side feature not yet
        implemented by the prosody plugin.
        @param mess_data: message data dictionary
        @param skip_send: set to True to skip sending the message to only store it
        @param profile: profile
        """
        try:
            client = self.profiles[profile]
        except KeyError:
            error(_("Trying to send a message with no profile"))
            return
        current_jid = client.jid
        if not skip_send:
            client.xmlstream.send(mess_data['xml'])
        if mess_data["type"] != "groupchat":
            # we don't add groupchat message to history, as we get them back
            # and they will be added then
            if mess_data['message']: # we need a message to save something
                self.memory.addToHistory(current_jid, mess_data['to'],
                                     unicode(mess_data["message"]),
                                     unicode(mess_data["type"]),
                                     mess_data['extra'],
                                     profile=profile)
                # We send back the message, so all clients are aware of it
                self.bridge.newMessage(mess_data['xml']['from'],
                                       unicode(mess_data["message"]),
                                       mess_type=mess_data["type"],
                                       to_jid=mess_data['xml']['to'],
                                       extra=mess_data['extra'],
                                       profile=profile)

    def _setPresence(self, to="", show="", priority=0, statuses=None, profile_key='@NONE@'):
        return self.setPresence(jid.JID(to) if to else None, show, priority, statuses, profile_key)

    def setPresence(self, to_jid=None, show="", priority=0, statuses=None, profile_key='@NONE@'):
        """Send our presence information"""
        if statuses is None:
            statuses = {}
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        self.profiles[profile].presence.available(to_jid, show, statuses, priority)
        #XXX: FIXME: temporary fix to work around openfire 3.7.0 bug (presence is not broadcasted to generating resource)
        if '' in statuses:
            statuses['default'] = statuses['']
            del statuses['']
        self.bridge.presenceUpdate(self.profiles[profile].jid.full(), show,
                                   int(priority), statuses, profile)

    def subscription(self, subs_type, raw_jid, profile_key):
        """Called to manage subscription
        @param subs_type: subsciption type (cf RFC 3921)
        @param raw_jid: unicode entity's jid
        @param profile_key: profile"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        to_jid = jid.JID(raw_jid)
        debug(_('subsciption request [%(subs_type)s] for %(jid)s') % {'subs_type': subs_type, 'jid': to_jid.full()})
        if subs_type == "subscribe":
            self.profiles[profile].presence.subscribe(to_jid)
        elif subs_type == "subscribed":
            self.profiles[profile].presence.subscribed(to_jid)
        elif subs_type == "unsubscribe":
            self.profiles[profile].presence.unsubscribe(to_jid)
        elif subs_type == "unsubscribed":
            self.profiles[profile].presence.unsubscribed(to_jid)

    def _addContact(self, to_jid_s, profile_key):
        return self.addContact(jid.JID(to_jid_s), profile_key)

    def addContact(self, to_jid, profile_key):
        """Add a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        #self.profiles[profile].roster.addItem(to_jid)  #XXX: disabled (cf http://wokkel.ik.nu/ticket/56))
        self.profiles[profile].presence.subscribe(to_jid)

    def _updateContact(self, to_jid_s, name, groups, profile_key):
        return self.updateContact(jid.JID(to_jid_s), name, groups, profile_key)

    def updateContact(self, to_jid, name, groups, profile_key):
        """update a contact in roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        groups = set(groups)
        roster_item = RosterItem(to_jid)
        roster_item.name = name or None
        roster_item.groups = set(groups)
        self.profiles[profile].roster.updateItem(roster_item)

    def _delContact(self, to_jid_s, profile_key):
        return self.delContact(jid.JID(to_jid_s), profile_key)

    def delContact(self, to_jid, profile_key):
        """Remove contact from roster list"""
        profile = self.memory.getProfileName(profile_key)
        assert(profile)
        self.profiles[profile].roster.removeItem(to_jid)
        self.profiles[profile].presence.unsubscribe(to_jid)

    def requestServerDisco(self, feature, jid_=None, cache_only=False, profile_key="@NONE"):
        """Discover if a server or its items offer a given feature
        @param feature: the feature to check
        @param jid_: the jid of the server, local server if None
        @param cache_only: expect the result to be in cache and don't actually
        make any request. This can be used anytime for requesting a feature on
        the local server because the data are cached for sure.
        @result: the Deferred entity jid offering the feature, or None
        """
        profile = self.memory.getProfileName(profile_key)

        if not profile:
            return defer.succeed(None)
        if jid_ is None:
            jid_ = self.getClientHostJid(profile)
            cache_only = True
        hasServerFeature = lambda entity: entity if self.memory.hasServerFeature(feature, entity, profile) else None

        def haveItemsFeature(dummy=None):
            entities = self.memory.getAllServerIdentities(jid_, profile)
            if entities is None:
                return None  # no cached data for this server
            for entity in entities:
                if hasServerFeature(entity):
                    return entity
            return None  # data are cached but no entity was found

        entity = hasServerFeature(jid_) or haveItemsFeature()
        if entity:
            return defer.succeed(entity)
        elif entity is False or cache_only:
            return defer.succeed(None)

        # data for this server are not in cache
        disco = self.profiles[profile].disco

        def errback(failure, method, jid_, profile):
            # the target server is not reachable
            logging.error("disco.%s on %s failed! [%s]" % (method.func_name, jid_.userhost(), profile))
            logging.error("reason: %s" % failure.getErrorMessage())
            if method == disco.requestInfo:
                features = self.memory.server_features.setdefault(profile, {})
                features.setdefault(jid_, [])
            elif method == disco.requestItems:
                identities = self.memory.server_identities.setdefault(profile, {})
                identities.setdefault(jid_, {})
            return failure

        def callback(d):
            if hasServerFeature(jid_):
                return jid_
            else:
                d2 = disco.requestItems(jid_).addCallback(self.serverDiscoItems, disco, jid_, profile)
                d2.addErrback(errback, disco.requestItems, jid_, profile)
                return d2.addCallback(haveItemsFeature)

        d = disco.requestInfo(jid_).addCallback(self.serverDisco, jid_, profile)
        d.addCallbacks(callback, errback, [], errbackArgs=[disco.requestInfo, jid_, profile])
        return d

    ## callbacks ##

    def serverDisco(self, disco, jid_=None, profile=None):
        """xep-0030 Discovery Protocol.
        @param disco: result of the disco info query
        @param jid_: the jid of the target server
        @param profile: profile of the user
        """
        if jid_ is None:
            jid_ = self.getClientHostJid(profile)
        debug(_("Requested disco info on %s") % jid_)
        for feature in disco.features:
            debug(_("Feature found: %s") % feature)
            self.memory.addServerFeature(feature, jid_, profile)
        for cat, type_ in disco.identities:
            debug(_("Identity found: [%(category)s/%(type)s] %(identity)s")
                  % {'category': cat, 'type': type_, 'identity': disco.identities[(cat, type_)]})

    def serverDiscoItems(self, disco_result, disco_client, jid_, profile, initialized=None):
        """xep-0030 Discovery Protocol.
        @param disco_result: result of the disco item querry
        @param disco_client: SatDiscoProtocol instance
        @param jid_: the jid of the target server
        @param profile: profile of the user
        @param initialized: deferred which must be chained when everything is done"""

        def _check_entity_cb(result, entity, jid_, profile):
            debug(_("Requested disco info on %s") % entity)
            for category, type_ in result.identities:
                debug(_('Identity added: (%(category)s,%(type)s) ==> %(entity)s [%(profile)s]')
                      % {'category': category, 'type': type_, 'entity': entity, 'profile': profile})
                self.memory.addServerIdentity(category, type_, entity, jid_, profile)
            for feature in result.features:
                self.memory.addServerFeature(feature, entity, profile)

        def _errback(result, entity, jid_, profile):
            warning(_("Can't get information on identity [%(entity)s] for profile [%(profile)s]") % {'entity': entity, 'profile': profile})

        defer_list = []
        for item in disco_result._items:
            if item.entity.full().count('.') == 1:  # XXX: workaround for a bug on jabberfr, tmp
                warning(_('Using jabberfr workaround, be sure your domain has at least two levels (e.g. "example.tld", not "example" alone)'))
                continue
            args = [item.entity, jid_, profile]
            defer_list.append(disco_client.requestInfo(item.entity).addCallbacks(_check_entity_cb, _errback, args, None, args))
        if initialized:
            defer.DeferredList(defer_list).chainDeferred(initialized)

    ## Generic HMI ##

    def actionResult(self, action_id, action_type, data, profile):
        """Send the result of an action
        @param action_id: same action_id used with action
        @param action_type: result action_type ("PARAM", "SUCCESS", "ERROR", "XMLUI")
        @param data: dictionary
        """
        self.bridge.actionResult(action_type, action_id, data, profile)

    def actionResultExt(self, action_id, action_type, data, profile):
        """Send the result of an action, extended version
        @param action_id: same action_id used with action
        @param action_type: result action_type /!\ only "DICT_DICT" for this method
        @param data: dictionary of dictionaries
        """
        if action_type != "DICT_DICT":
            error(_("action_type for actionResultExt must be DICT_DICT, fixing it"))
            action_type = "DICT_DICT"
        self.bridge.actionResultExt(action_type, action_id, data, profile)

    def askConfirmation(self, conf_id, conf_type, data, cb, profile):
        """Add a confirmation callback
        @param conf_id: conf_id used to get answer
        @param conf_type: confirmation conf_type ("YES/NO", "FILE_TRANSFER")
        @param data: data (depend of confirmation conf_type)
        @param cb: callback called with the answer
        """
        # FIXME: use XMLUI and *callback methods for dialog
        client = self.getClient(profile)
        if not client:
            raise exceptions.ProfileUnknownError(_("Asking confirmation a non-existant profile"))
        if conf_id in client._waiting_conf:
            error(_("Attempt to register two callbacks for the same confirmation"))
        else:
            client._waiting_conf[conf_id] = (conf_type, data, cb)
            self.bridge.askConfirmation(conf_id, conf_type, data, profile)

    def confirmationAnswer(self, conf_id, accepted, data, profile):
        """Called by frontends to answer confirmation requests"""
        client = self.getClient(profile)
        if not client:
            raise exceptions.ProfileUnknownError(_("Confirmation answer from a non-existant profile"))
        debug(_("Received confirmation answer for conf_id [%(conf_id)s]: %(success)s") % {'conf_id': conf_id, 'success': _("accepted") if accepted else _("refused")})
        if conf_id not in client._waiting_conf:
            error(_("Received an unknown confirmation (%(id)s for %(profile)s)") % {'id': conf_id, 'profile': profile})
        else:
            cb = client._waiting_conf[conf_id][-1]
            del client._waiting_conf[conf_id]
            cb(conf_id, accepted, data, profile)

    def registerProgressCB(self, progress_id, CB, profile):
        """Register a callback called when progress is requested for id"""
        client = self.getClient(profile)
        if not client:
            raise exceptions.ProfileUnknownError
        client._progress_cb_map[progress_id] = CB

    def removeProgressCB(self, progress_id, profile):
        """Remove a progress callback"""
        client = self.getClient(profile)
        if not client:
            raise exceptions.ProfileUnknownError
        if progress_id not in client._progress_cb_map:
            error(_("Trying to remove an unknow progress callback"))
        else:
            del client._progress_cb_map[progress_id]

    def getProgress(self, progress_id, profile):
        """Return a dict with progress information
        data['position'] : current possition
        data['size'] : end_position
        """
        client = self.getClient(profile)
        if not profile:
            raise exceptions.ProfileNotInCacheError
        data = {}
        try:
            client._progress_cb_map[progress_id](progress_id, data, profile)
        except KeyError:
            pass
            #debug("Requested progress for unknown progress_id")
        return data

    def registerCallback(self, callback, *args, **kwargs):
        """ Register a callback.
        Use with_data=True in kwargs if the callback use the optional data dict
        use force_id=id to avoid generated id. Can lead to name conflict, avoid if possible
        use one_shot=True to delete callback once it have been called
        @param callback: any callable
        @return: id of the registered callback
        """
        callback_id = kwargs.pop('force_id', None)
        if callback_id is None:
            callback_id = str(uuid4())
        else:
            if callback_id in self._cb_map:
                raise exceptions.ConflictError(_(u"id already registered"))
        self._cb_map[callback_id] = (callback, args, kwargs)

        if "one_shot" in kwargs: # One Shot callback are removed after 30 min
            def purgeCallback():
                try:
                    self.removeCallback(callback_id)
                except KeyError:
                    pass
            reactor.callLater(1800, purgeCallback)

        return callback_id

    def removeCallback(self, callback_id):
        """ Remove a previously registered callback
        @param callback_id: id returned by [registerCallback] """
        debug("Removing callback [%s]" % callback_id)
        del self._cb_map[callback_id]

    def launchCallback(self, callback_id, data=None, profile_key="@NONE@"):
        """Launch a specific callback
        @param callback_id: id of the action (callback) to launch
        @param data: optional data
        @profile_key: %(doc_profile_key)s
        @return: a deferred which fire a dict where key can be:
            - xmlui: a XMLUI need to be displayed
        """
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileUnknownError(_('trying to launch action with a non-existant profile'))

        try:
            callback, args, kwargs = self._cb_map[callback_id]
        except KeyError:
            raise exceptions.DataError("Unknown callback id")

        if kwargs.get("with_data", False):
            if data is None:
                raise exceptions.DataError("Required data for this callback is missing")
            args,kwargs=list(args)[:],kwargs.copy() # we don't want to modify the original (kw)args
            args.insert(0, data)
            kwargs["profile"] = profile
            del kwargs["with_data"]

        if kwargs.pop('one_shot', False):
            self.removeCallback(callback_id)

        return defer.maybeDeferred(callback, *args, **kwargs)

    #Menus management

    def importMenu(self, path, callback, security_limit=NO_SECURITY_LIMIT, help_string="", type_="NORMAL"):
        """register a new menu for frontends
        @param path: path to go to the menu (category/subcategory/.../item), must be an iterable (e.g.: ("File", "Open"))
            /!\ use D_() instead of _() for translations (e.g. (D_("File"), D_("Open")))
        @param callback: method to be called when menuitem is selected, callable or a callback id (string) as returned by [registerCallback]
        @param security_limit: %(doc_security_limit)s
            /!\ security_limit MUST be added to data in launchCallback if used #TODO
        @param help_string: string used to indicate what the menu do (can be show as a tooltip).
            /!\ use D_() instead of _() for translations
        @param type: one of:
            - GLOBAL: classical menu, can be shown in a menubar on top (e.g. something like File/Open)
            - ROOM: like a global menu, but only shown in multi-user chat
            - JID_CONTEXT: contextual menu, used with any jid (e.g.: ad hoc commands, jid is already filled)
            - ROSTER_JID_CONTEXT: like JID_CONTEXT, but restricted to jids in roster.
            - ROSTER_GROUP_CONTEXT: contextual menu, used with group (e.g.: publish microblog, group is already filled)
        @return: menu_id (same as callback_id)
        """

        if callable(callback):
            callback_id = self.registerCallback(callback, with_data=True)
        elif isinstance(callback, basestring):
            # The callback is already registered
            callback_id = callback
            try:
                callback, args, kwargs = self._cb_map[callback_id]
            except KeyError:
                raise exceptions.DataError("Unknown callback id")
            kwargs["with_data"] = True # we have to be sure that we use extra data
        else:
            raise exceptions.DataError("Unknown callback type")

        for menu_data in self._menus.itervalues():
            if menu_data['path'] == path and menu_data['type'] == type_:
                raise exceptions.ConflictError(_("A menu with the same path and type already exists"))

        menu_data = {'path': path,
                     'security_limit': security_limit,
                     'help_string': help_string,
                     'type': type_
                    }

        self._menus[callback_id] = menu_data

        return callback_id

    def getMenus(self, language='', security_limit=NO_SECURITY_LIMIT):
        """Return all menus registered
        @param language: language used for translation, or empty string for default
        @param security_limit: %(doc_security_limit)s
        @return: array of tuple with:
            - menu id (same as callback_id)
            - menu type
            - raw menu path (array of strings)
            - translated menu path

        """
        ret = []
        for menu_id, menu_data in self._menus.iteritems():
            type_ = menu_data['type']
            path = menu_data['path']
            menu_security_limit = menu_data['security_limit']
            if security_limit!=NO_SECURITY_LIMIT and (menu_security_limit==NO_SECURITY_LIMIT or menu_security_limit>security_limit):
                continue
            languageSwitch(language)
            path_i18n = [_(elt) for elt in path]
            languageSwitch()
            ret.append((menu_id, type_, path, path_i18n))

        return ret

    def getMenuHelp(self, menu_id, language=''):
        """
        return the help string of the menu
        @param menu_id: id of the menu (same as callback_id)
        @param language: language used for translation, or empty string for default
        @param return: translated help

        """
        try:
            menu_data = self._menus[menu_id]
        except KeyError:
            raise exceptions.DataError("Trying to access an unknown menu")
        languageSwitch(language)
        help_string = _(menu_data['help_string'])
        languageSwitch()
        return help_string
