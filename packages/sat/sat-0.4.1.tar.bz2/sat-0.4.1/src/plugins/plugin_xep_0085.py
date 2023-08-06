#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for Chat State Notifications Protocol (xep-0085)
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Adrien Cossa (souliane@mailoo.org)

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
from sat.core import exceptions
from logging import info
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber.jid import JID
try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from threading import Timer
from twisted.words.xish import domish

NS_XMPP_CLIENT = "jabber:client"
NS_CHAT_STATES = "http://jabber.org/protocol/chatstates"
CHAT_STATES = ["active", "inactive", "gone", "composing", "paused"]
MESSAGE_TYPES = ["chat", "groupchat"]
PARAM_KEY = "Notifications"
PARAM_NAME = "Enable chat state notifications"
ENTITY_KEY = PARAM_KEY + "_" + PARAM_NAME

PLUGIN_INFO = {
    "name": "Chat State Notifications Protocol Plugin",
    "import_name": "XEP-0085",
    "type": "XEP",
    "protocols": ["XEP-0085"],
    "dependencies": [],
    "main": "XEP_0085",
    "handler": "yes",
    "description": _("""Implementation of Chat State Notifications Protocol""")
}


# Describe the internal transitions that are triggered
# by a timer. Beside that, external transitions can be
# runned to target the states "active" or "composing".
# Delay is specified here in seconds.
TRANSITIONS = {
    "active": {"next_state": "inactive", "delay": 120},
    "inactive": {"next_state": "gone", "delay": 480},
    "gone": {"next_state": "", "delay": 0},
    "composing": {"next_state": "paused", "delay": 30},
    "paused": {"next_state": "inactive", "delay": 450}
}


class UnknownChatStateException(Exception):
    """
    This error is raised when an unknown chat state is used.
    """
    pass


class XEP_0085(object):
    """
    Implementation for XEP 0085
    """
    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(param_name)s" label="%(param_label)s" value="true" type="bool" security="0"/>
     </category>
    </individual>
    </params>
    """ % {
        'category_name': PARAM_KEY,
        'category_label': _(PARAM_KEY),
        'param_name': PARAM_NAME,
        'param_label': _('Enable chat state notifications')
    }

    def __init__(self, host):
        info(_("Chat State Notifications plugin initialization"))
        self.host = host

        # parameter value is retrieved before each use
        host.memory.updateParams(self.params)

        # triggers from core
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)
        host.trigger.add("sendMessage", self.sendMessageTrigger)
        host.trigger.add("paramUpdateTrigger", self.paramUpdateTrigger)
        # TODO: handle profile disconnection (free memory in entity data)

        # args: to_s (jid as string), profile
        host.bridge.addMethod("chatStateComposing", ".plugin", in_sign='ss',
                              out_sign='', method=self.chatStateComposing)

        # args: from (jid as string), state in CHAT_STATES, profile
        host.bridge.addSignal("chatStateReceived", ".plugin", signature='sss')

    def getHandler(self, profile):
        return XEP_0085_handler(self, profile)

    def updateEntityData(self, entity_jid, value, profile):
        """
        Update the entity data of the given profile for one or all contacts.
        Reset the chat state(s) display if the notification has been disabled.
        @param entity_jid: contact's JID, or '@ALL@' to update all contacts.
        @param value: True, False or '@NONE@' to delete the entity data
        @param profile: current profile
        """
        self.host.memory.updateEntityData(entity_jid, ENTITY_KEY, value, profile)
        if not value or value == "@NONE@":
            # disable chat state for this or these contact(s)
            self.host.bridge.chatStateReceived(unicode(entity_jid), "", profile)

    def paramUpdateTrigger(self, name, value, category, type, profile):
        """
        Reset all the existing chat state entity data associated with this profile after a parameter modification.
        @param name: parameter name
        @param value: "true" to activate the notifications, or any other value to delete it
        @param category: parameter category
        """
        if (category, name) == (PARAM_KEY, PARAM_NAME):
            self.updateEntityData("@ALL@", True if value == "true" else "@NONE@", profile)
            return False
        return True


    def messageReceivedTrigger(self, message, post_treat, profile):
        """
        Update the entity cache when we receive a message with body.
        Check for a check state in the incoming message and broadcast signal.
        """
        if not self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile):
            return True

        try:
            domish.generateElementsNamed(message.elements(), name="body").next()
            from_jid = JID(message.getAttribute("from"))
            try:
                domish.generateElementsNamed(message.elements(), name="active").next()
                # contact enabled Chat State Notifications
                self.updateEntityData(from_jid, True, profile)
                # init to send following "composing" state
                self.__chatStateInit(from_jid, message.getAttribute("type"), profile)
            except StopIteration:
                # contact didn't enable Chat State Notifications
                self.updateEntityData(from_jid, False, profile)
                return True
        except StopIteration:
            pass

        state_list = [child.name for child in message.elements() if
                      message.getAttribute("type") in MESSAGE_TYPES
                      and child.name in CHAT_STATES
                      and child.defaultUri == NS_CHAT_STATES]
        for state in state_list:
            # there must be only one state according to the XEP
            self.host.bridge.chatStateReceived(message.getAttribute("from"), state, profile)
            break
        return True

    def sendMessageTrigger(self, mess_data, treatments, profile):
        """
        Eventually add the chat state to the message and initiate
        the state machine when sending an "active" state.
        """
        def treatment(mess_data):
            message = mess_data['xml']
            to_jid = JID(message.getAttribute("to"))
            if not self.__checkActivation(to_jid, forceEntityData=True, profile=profile):
                return mess_data
            try:
                # message with a body always mean active state
                domish.generateElementsNamed(message.elements(), name="body").next()
                message.addElement('active', NS_CHAT_STATES)
                # launch the chat state machine (init the timer)
                self.__chatStateActive(to_jid, mess_data["type"], profile)
            except StopIteration:
                if "chat_state" in mess_data["extra"]:
                    state = mess_data["extra"].pop("chat_state")
                    assert(state in CHAT_STATES)
                    message.addElement(state, NS_CHAT_STATES)
            return mess_data

        treatments.addCallback(treatment)
        return True

    def __checkActivation(self, to_jid, forceEntityData, profile):
        """
        @param to_joid: the contact's JID
        @param forceEntityData: if set to True, a non-existing
        entity data will be considered to be True (and initialized)
        @param: current profile
        @return: True if the notifications should be sent to this JID.
        """
        # check if the parameter is active
        if not self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile):
            return False
        # check if notifications should be sent to this contact
        try:
            return self.host.memory.getEntityData(to_jid, [ENTITY_KEY], profile)[ENTITY_KEY]
        except (exceptions.UnknownEntityError, KeyError):
            if forceEntityData:
                # enable it for the first time
                self.updateEntityData(to_jid, True, profile)
                return True
        # wait for the first message before sending states
        return False

    def __chatStateInit(self, to_jid, mess_type, profile):
        """
        Data initialization for the chat state machine.
        """
        # TODO: use also the resource in map key
        to_jid = to_jid.userhostJID()
        if mess_type is None:
            return
        if not hasattr(self, "map"):
            self.map = {}
        profile_map = self.map.setdefault(profile, {})
        if not to_jid in profile_map:
            machine = ChatStateMachine(self.host, to_jid,
                                       mess_type, profile)
            self.map[profile][to_jid] = machine

    def __chatStateActive(self, to_jid, mess_type, profile_key):
        """
        Launch the chat state machine on "active" state.
        """
        # TODO: use also the JID resource in the map key
        to_jid = to_jid.userhostJID()
        profile = self.host.memory.getProfileName(profile_key)
        if profile is None:
            raise exceptions.ProfileUnknownError
            return
        self.__chatStateInit(to_jid, mess_type, profile)
        self.map[profile][to_jid]._onEvent("active")

    def chatStateComposing(self, to_jid_s, profile_key):
        """
        Move to the "composing" state. Since this method is called
        from the front-end, it needs to check the values of the
        parameter "Send chat state notifications" and the entity
        data associated to the target JID.
        TODO: try to optimize this method which is called often
        """
        # TODO: use also the JID resource in the map key
        to_jid = JID(to_jid_s).userhostJID()
        profile = self.host.memory.getProfileName(profile_key)
        if profile is None:
            raise exceptions.ProfileUnknownError
            return
        if not self.__checkActivation(to_jid, forceEntityData=False, profile=profile):
            return
        try:
            self.map[profile][to_jid]._onEvent("composing")
        except AttributeError:
            # no message has been sent/received since the notifications
            # have been enabled, it's better to wait for a first one
            pass


class ChatStateMachine:
    """
    This class represents a chat state, between one profile and
    one target contact. A timer is used to move from one state
    to the other. The initialization is done through the "active"
    state which is internally set when a message is sent. The state
    "composing" can be set externally (through the bridge by a
    frontend). Other states are automatically set with the timer.
    """

    def __init__(self, host, to_jid, mess_type, profile):
        """
        Initialization need to store the target, message type
        and a profile for sending later messages.
        """
        self.host = host
        self.to_jid = to_jid
        self.mess_type = mess_type
        self.profile = profile
        self.state = None
        self.timer = None

    def _onEvent(self, state):
        """
        Move to the specified state, eventually send the
        notification to the contact (the "active" state is
        automatically sent with each message) and set the timer.
        """
        if state != self.state and state != "active":
            # send a new message without body
            self.host.sendMessage(self.to_jid,
                                  '',
                                  '',
                                  self.mess_type,
                                  extra={"chat_state": state},
                                  profile_key=self.profile)
        self.state = state
        if not self.timer is None:
            self.timer.cancel()

        if not state in TRANSITIONS:
            return
        if not "next_state" in TRANSITIONS[state]:
            return
        if not "delay" in TRANSITIONS[state]:
            return
        next_state = TRANSITIONS[state]["next_state"]
        delay = TRANSITIONS[state]["delay"]
        if next_state == "" or delay < 0:
            return
        self.timer = Timer(delay, self._onEvent, [next_state])
        self.timer.start()


class XEP_0085_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_CHAT_STATES)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
