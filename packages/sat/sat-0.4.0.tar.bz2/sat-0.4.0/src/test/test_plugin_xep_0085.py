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

""" Plugin chat states notification tests """

from constants import Const
from sat.test import helpers
from sat.plugins import plugin_xep_0085 as plugin
from sat.memory.memory import NO_SECURITY_LIMIT
from copy import deepcopy
from twisted.internet import defer
from wokkel.generic import parseXml
from twisted.words.protocols.jabber.jid import JID


class XEP_0085Test(helpers.SatTestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = plugin.XEP_0085(self.host)

    def test_messageReceived(self):
        self.host.memory.init()
        self.host.memory.setParam(plugin.PARAM_NAME, True, plugin.PARAM_KEY, NO_SECURITY_LIMIT, Const.PROFILE[0])
        for state in plugin.CHAT_STATES:
            xml = u"""
            <message type="chat" from="%s" to="%s" id="test_1">
            %s
            <%s xmlns='%s'/>
            </message>
            """ % (Const.JID_STR[1],
                   Const.JID_STR[0],
                   "<body>test</body>" if state == "active" else "",
                   state, plugin.NS_CHAT_STATES)
            stanza = parseXml(xml.encode("utf-8"))
            self.host.bridge.expectCall("chatStateReceived", Const.JID_STR[1], state, Const.PROFILE[0])
            self.plugin.messageReceivedTrigger(stanza, defer.Deferred(), Const.PROFILE[0])

    def test_sendMessageTrigger(self):
        self.host.memory.init()
        self.host.memory.setParam(plugin.PARAM_NAME, True, plugin.PARAM_KEY, NO_SECURITY_LIMIT, Const.PROFILE[0])
        for state in plugin.CHAT_STATES:
            mess_data = {"to": Const.JID[0],
                         "type": "chat",
                         "message": "content",
                         "extra": {} if state == "active" else {"chat_state": state}}
            stanza = u"""
            <message type="chat" from="%s" to="%s" id="test_1">
            %s
            </message>
            """ % (Const.JID_STR[1], Const.JID_STR[0],
                   ("<body>%s</body>" % mess_data['message']) if state == "active" else "")
            mess_data['xml'] = parseXml(stanza.encode("utf-8"))
            expected = deepcopy(mess_data['xml'])
            expected.addElement(state, plugin.NS_CHAT_STATES)
            treatments = defer.Deferred()
            self.plugin.sendMessageTrigger(mess_data, treatments, Const.PROFILE[0])
            xml = treatments.callbacks[0][0][0](mess_data)
            # cancel the timer to not block the process
            self.plugin.map[Const.PROFILE[0]][Const.JID[0].userhostJID()].timer.cancel()
            self.assertEqualXML(xml['xml'].toXml().encode("utf-8"), expected.toXml().encode("utf-8"))
