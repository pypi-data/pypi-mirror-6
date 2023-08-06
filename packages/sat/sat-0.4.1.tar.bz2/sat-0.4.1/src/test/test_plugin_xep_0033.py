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

""" Plugin extended addressing stanzas """

from constants import Const
from sat.test import helpers
from sat.plugins import plugin_xep_0033 as plugin
from sat.memory.memory import NO_SECURITY_LIMIT
from sat.core.sat_main import AbortSendMessage, MessageSentAndStored
from copy import deepcopy
from twisted.internet import defer
from wokkel.generic import parseXml
from twisted.words.protocols.jabber.jid import JID
import logging


class XEP_0033Test(helpers.SatTestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()
        self.plugin = plugin.XEP_0033(self.host)

    def test_messageReceived(self):
        self.host.memory.init()
        xml = u"""
        <message type="chat" from="%s" to="%s" id="test_1">
            <body>test</body>
            <addresses xmlns='http://jabber.org/protocol/address'>
                <address type='to' jid='%s'/>
                <address type='cc' jid='%s'/>
                <address type='bcc' jid='%s'/>
            </addresses>
        </message>
        """ % (Const.JID_STR[1], self.host.getClientHostJid(Const.PROFILE[0]),
               Const.JID_STR[0], Const.JID_STR[1], Const.JID_STR[2])
        stanza = parseXml(xml.encode("utf-8"))
        treatments = defer.Deferred()
        self.plugin.messageReceivedTrigger(stanza, treatments, Const.PROFILE[0])
        data = {'extra': {}}

        def cb(data):
            expected = ('to', Const.JID_STR[0], 'cc', Const.JID_STR[1], 'bcc', Const.JID_STR[2])
            msg = 'Expected: %s\nGot:      %s' % (expected, data['extra']['addresses'])
            self.assertEqual(data['extra']['addresses'], '%s:%s\n%s:%s\n%s:%s\n' % expected, msg)

        treatments.addCallback(cb)
        treatments.callback(data)

    def test_sendMessageTrigger(self):
        mess_data = {"to": self.host.getClientHostJid(Const.PROFILE[0]),
                     "type": "chat",
                     "message": "content",
                     "extra": {}
                     }
        addresses = ('to', Const.JID_STR[0], 'cc', Const.JID_STR[1], 'bcc', Const.JID_STR[2])
        mess_data["extra"]["address"] = '%s:%s\n%s:%s\n%s:%s\n' % addresses
        original_stanza = u"""
        <message type="chat" from="%s" to="%s" id="test_1">
            <body>content</body>
        </message>
        """ % (Const.JID_STR[1], self.host.getClientHostJid(Const.PROFILE[0]))
        mess_data['xml'] = parseXml(original_stanza.encode("utf-8"))
        expected = deepcopy(mess_data['xml'])
        addresses_extra = """
        <addresses xmlns='http://jabber.org/protocol/address'>
            <address type='%s' jid='%s'/>
            <address type='%s' jid='%s'/>
            <address type='%s' jid='%s'/>
        </addresses>""" % addresses
        addresses_element = parseXml(addresses_extra.encode('utf-8'))
        expected.addChild(addresses_element)

        def assertAddresses(mess_data):
            """The mess_data that we got here has been modified by self.plugin.sendMessageTrigger,
            check that the addresses element has been added to the stanza."""
            self.assertEqualXML(mess_data['xml'].toXml().encode("utf-8"), expected.toXml().encode("utf-8"))

        def sendMessageErrback(failure, exception_class):
            """If the failure does encapsulate the expected exception, it will be silently
            trapped, otherwise it will be re-raised and will make the test fail"""
            if exception_class == MessageSentAndStored:
                assertAddresses(failure.value.mess_data)
            failure.trap(exception_class)

        def checkSentAndStored():
            """Check that all the recipients got their messages and that the history has been filled.
            /!\ see the comments in XEP_0033.sendAndStoreMessage"""
            sent = []
            stored = []
            cache = set()
            for to_s in [addresses[1], addresses[3], addresses[5]]:
                to_jid = JID(to_s)
                host = JID(to_jid.host)
                logger = logging.getLogger()
                level = logger.getEffectiveLevel()
                logger.setLevel(logging.ERROR)  # remove warning pollution
                if self.host.memory.hasServerFeature(plugin.NS_ADDRESS, host, Const.PROFILE[0]):
                    if host not in cache:
                        sent.append(host)
                        stored.append(host)
                        cache.add(host)
                    stored.append(to_jid)
                else:
                    sent.append(to_jid)
                    stored.append(to_jid)
                logger.setLevel(level)
            msg = "/!\ see the comments in XEP_0033.sendAndStoreMessage"
            self.assertEqualUnsortedList(self.host.sent_messages, sent, msg)
            self.assertEqualUnsortedList(self.host.stored_messages, stored, msg)

        def trigger(treatments, data, *args):
            logger = logging.getLogger()
            level = logger.getEffectiveLevel()
            logger.setLevel(logging.ERROR)  # remove warning pollution
            self.plugin.sendMessageTrigger(*args)
            treatments.callback(data)
            logger.setLevel(level)

        # feature is not supported, abort the message
        self.host.memory.init()
        treatments = defer.Deferred()
        data = deepcopy(mess_data)
        trigger(treatments, data, data, treatments, Const.PROFILE[0])
        treatments.addCallbacks(assertAddresses, lambda failure: sendMessageErrback(failure, AbortSendMessage))

        # feature is supported
        self.host.init()
        self.host.memory.init()
        self.host.memory.addServerFeature(plugin.NS_ADDRESS, self.host.getClientHostJid(Const.PROFILE[0]), Const.PROFILE[0])
        treatments = defer.Deferred()
        data = deepcopy(mess_data)
        trigger(treatments, data, data, treatments, Const.PROFILE[0])
        treatments.addCallbacks(assertAddresses, lambda failure: sendMessageErrback(failure, MessageSentAndStored))
        checkSentAndStored()

        # check that a wrong recipient entity is fixed by the backend
        self.host.init()
        self.host.memory.init()
        self.host.memory.addServerFeature(plugin.NS_ADDRESS, self.host.getClientHostJid(Const.PROFILE[0]), Const.PROFILE[0])
        treatments = defer.Deferred()
        data = deepcopy(mess_data)
        data["to"] = Const.JID[0]
        trigger(treatments, mess_data, data, treatments, Const.PROFILE[0])
        treatments.addCallbacks(assertAddresses, lambda failure: sendMessageErrback(failure, MessageSentAndStored))
        checkSentAndStored()
