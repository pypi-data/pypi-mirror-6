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
from sat.core import exceptions
from constants import Const
from wokkel.xmppim import RosterItem
from sat.core.xmpp import SatRosterProtocol
from sat.memory.memory import Params, Memory
from twisted.trial.unittest import FailTest
from twisted.trial import unittest
from twisted.internet import defer
from twisted.words.protocols.jabber.jid import JID
from xml.etree import cElementTree as etree
from collections import Counter
import re


def b2s(value):
    """Convert a bool to a unicode string used in bridge
    @param value: boolean value
    @return: unicode conversion, according to bridge convention

    """
    return  u"True" if value else u"False"


class DifferentArgsException(FailTest):
    pass


class DifferentXMLException(FailTest):
    pass


class DifferentListException(FailTest):
    pass


class FakeSAT(object):
    """Class to simulate a SAT instance"""

    def __init__(self):
        self.bridge = FakeBridge()
        self.memory = FakeMemory(self)
        self.trigger = FakeTriggerManager()
        self.init()

    def init(self):
        """This can be called by tests that check for sent and stored messages,
        uses FakeClient or get/set some other data that need to be cleaned"""
        self.sent_messages = []
        self.stored_messages = []
        self.plugins = {}
        self.profiles = {}

    def delContact(self, to, profile_key):
        #TODO
        pass

    def registerCallback(self, callback, *args, **kwargs):
        pass

    def registerNewAccountCB(self, data, profile):
        pass

    def sendMessage(self, to_s, msg, subject=None, mess_type='auto', extra={}, profile_key='@NONE@'):
        self.sendAndStoreMessage({"to": JID(to_s)})

    def sendAndStoreMessage(self, mess_data, skip_send=False, profile=None):
        """Save the information to check later to whom messages have been sent and
        if entries have been added to the history"""
        if not skip_send:
            self.sent_messages.append(mess_data["to"])
        self.stored_messages.append(mess_data["to"])
        pass

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
        self.memory.server_features.setdefault(profile, {})
        if jid_ is None:
            jid_ = self.getClientHostJid(profile_key)
        # call FakeMemory.init and FakeMemory.addServerFeature
        # in your tests to change the return value of this method
        return defer.succeed(jid_ if self.memory.hasServerFeature(feature, jid_, profile_key) else None)

    def getClientHostJid(self, profile_key):
        return Const.PROFILE_DICT[profile_key].host

    def getClient(self, profile_key):
        """Convenient method to get client from profile key
        @return: client or None if it doesn't exist"""
        profile = self.memory.getProfileName(profile_key)
        if not profile:
            return None
        if profile not in self.profiles:
            self.profiles[profile] = FakeClient(self, profile)
            self.profiles[profile].client_initialized.callback(None)
        return self.profiles[profile]

    def getJidNStream(self, profile_key):
        """Convenient method to get jid and stream from profile key
        @return: tuple (jid, xmlstream) from profile, can be None"""
        return (Const.PROFILE_DICT[profile_key], None)

    def isConnected(self, profile):
        return True

    def getSentMessageRaw(self, profile_index):
        """Pop and return the sent message in first position (works like a FIFO).
        Called by tests. FakeClient instances associated to each profile must have
        been previously initialized with the method FakeSAT.getClient.
        @return: the sent message for given profile, or None"""
        try:
            return self.profiles[Const.PROFILE[profile_index]].xmlstream.sent.pop(0)
        except IndexError:
            return None

    def getSentMessage(self, profile_index):
        """Pop and return the sent message in first position (works like a FIFO).
        Called by tests. FakeClient instances associated to each profile must have
        been previously initialized with the method FakeSAT.getClient.
        @return: XML representation of the sent message for given profile, or None"""
        entry = self.getSentMessageRaw(profile_index)
        return entry.toXml() if entry else None


class FakeBridge(object):
    """Class to simulate and test bridge calls"""

    def __init__(self):
        self.expected_calls = {}

    def expectCall(self, name, *check_args, **check_kwargs):
        if hasattr(self, name):  # queue this new call as one already exists
            self.expected_calls.setdefault(name, [])
            self.expected_calls[name].append((check_args, check_kwargs))
            return

        def checkCall(*args, **kwargs):
            if args != check_args or kwargs != check_kwargs:
                print "\n\n--------------------"
                print "Args are not equals:"
                print "args\n----\n%s (sent)\n%s (wanted)" % (args, check_args)
                print "kwargs\n------\n%s (sent)\n%s (wanted)" % (kwargs, check_kwargs)
                print "--------------------\n\n"
                raise DifferentArgsException
            delattr(self, name)

            if name in self.expected_calls:  # register the next call
                args, kwargs = self.expected_calls[name].pop(0)
                if len(self.expected_calls[name]) == 0:
                    del self.expected_calls[name]
                self.expectCall(name, *args, **kwargs)

        setattr(self, name, checkCall)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc=None):
        pass

    def addSignal(self, name, int_suffix, signature):
        pass

    def addTestCallback(self, name, method):
        """This can be used to register callbacks for bridge methods AND signals.
        Contrary to expectCall, this will not check if the method or signal is
        called/sent with the correct arguments, it will instead run the callback
        of your choice."""
        setattr(self, name, method)


class FakeParams(Params):
    """Class to simulate and test params object. The methods of Params that could
    not be run (for example those using the storage attribute must be overwritten
    by a naive simulation of what they should do."""

    def __init__(self, host, storage):
        Params.__init__(self, host, storage)
        self.params = {}  # naive simulation of values storage

    def setParam(self, name, value, category, security_limit=-1, profile_key='@NONE@'):
        profile = self.getProfileName(profile_key)
        self.params.setdefault(profile, {})
        self.params[profile_key][(category, name)] = value

    def getParamA(self, name, category, attr="value", profile_key='@NONE@'):
        profile = self.getProfileName(profile_key)
        return self.params[profile][(category, name)]

    def getProfileName(self, profile_key, return_profile_keys=False):
        if profile_key == '@DEFAULT@':
            return Const.PROFILE[0]
        elif profile_key == '@NONE@':
            raise exceptions.ProfileNotSetError
        else:
            return profile_key

    def loadIndParams(self, profile, cache=None):
        self.params[profile] = {}
        return defer.succeed(None)


class FakeMemory(Memory):
    """Class to simulate and test memory object"""

    def __init__(self, host):
        # do not call Memory.__init__, we just want to call the methods that are
        # manipulating basic stuff, the others should be overwritten when needed
        self.host = host
        self.params = FakeParams(host, None)
        self.config = self.parseMainConf()
        self.init()

    def init(self):
        """Tests that manipulate params, entities, features should
        re-initialise the memory first to not fake the result."""
        self.params.load_default_params()
        self.params.params.clear()
        self.params.frontends_cache = []
        self.entities_data = {}
        self.server_features = {}

    def getProfileName(self, profile_key, return_profile_keys=False):
        return self.params.getProfileName(profile_key, return_profile_keys)

    def addToHistory(self, from_jid, to_jid, message, _type='chat', extra=None, timestamp=None, profile="@NONE@"):
        pass

    def addContact(self, contact_jid, attributes, groups, profile_key='@DEFAULT@'):
        pass

    def setPresenceStatus(self, contact_jid, show, priority, statuses, profile_key='@DEFAULT@'):
        pass

    def addWaitingSub(self, type_, contact_jid, profile_key):
        pass

    def delWaitingSub(self, contact_jid, profile_key):
        pass

    def updateEntityData(self, entity_jid, key, value, profile_key):
        self.entities_data.setdefault(entity_jid, {})
        self.entities_data[entity_jid][key] = value

    def getEntityData(self, entity_jid, keys, profile_key):
        result = {}
        for key in keys:
            result[key] = self.entities_data[entity_jid][key]
        return result


class FakeTriggerManager(object):

    def add(self, point_name, callback, priority=0):
        pass

    def point(self, point_name, *args, **kwargs):
        """We always return true to continue the action"""
        return True


class FakeRosterProtocol(SatRosterProtocol):
    """This class is used by FakeClient (one instance per profile)"""

    def __init__(self, host, parent):
        SatRosterProtocol.__init__(self, host)
        self.parent = parent
        self.addItem(parent.jid)

    def addItem(self, jid, *args, **kwargs):
        if not args and not kwargs:
            # defaults values setted for the tests only
            kwargs["subscriptionTo"] = True
            kwargs["subscriptionFrom"] = True
        roster_item = RosterItem(jid, *args, **kwargs)
        attrs = {'to': b2s(roster_item.subscriptionTo), 'from': b2s(roster_item.subscriptionFrom), 'ask': b2s(roster_item.pendingOut)}
        if roster_item.name:
            attrs['name'] = roster_item.name
        self.host.bridge.expectCall("newContact", jid.full(), attrs, roster_item.groups, self.parent.profile)
        self.onRosterSet(roster_item)


class FakeXmlStream(object):
    """This class is used by FakeClient (one instance per profile)"""

    def __init__(self):
        self.sent = []

    def send(self, obj):
        """Save the sent messages to compare them later"""
        self.sent.append(obj)
        return defer.succeed(None)


class FakeClient(object):
    """Tests involving more than one profile need one instance of this class per profile"""

    def __init__(self, host, profile=None):
        self.host = host
        self.profile = profile if profile else Const.PROFILE[0]
        self.jid = Const.PROFILE_DICT[self.profile]
        self.roster = FakeRosterProtocol(host, self)
        self.client_initialized = defer.Deferred()
        self.xmlstream = FakeXmlStream()

    def send(self, obj):
        return self.xmlstream.send(obj)


class SatTestCase(unittest.TestCase):

    def assertEqualXML(self, xml, expected, ignore_blank=False):
        def equalElt(got_elt, exp_elt):
            if ignore_blank:
                for elt in got_elt, exp_elt:
                    for attr in ('text', 'tail'):
                        value = getattr(elt, attr)
                        try:
                            value = value.strip() or None
                        except AttributeError:
                            value = None
                        setattr(elt, attr, value)
            if (got_elt.tag != exp_elt.tag):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "tag: got [%s] expected: [%s]" % (got_elt.tag, exp_elt.tag)
                return False
            if (got_elt.attrib != exp_elt.attrib):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "attribs: got %s expected %s" % (got_elt.attrib, exp_elt.attrib)
                return False
            if (got_elt.tail != exp_elt.tail or got_elt.text != exp_elt.text):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "text: got [%s] expected: [%s]" % (got_elt.text, exp_elt.text)
                print "tail: got [%s] expected: [%s]" % (got_elt.tail, exp_elt.tail)
                return False
            if (len(got_elt) != len(exp_elt)):
                print "XML are not equals (elt %s/%s):" % (got_elt, exp_elt)
                print "children len: got %d expected: %d" % (len(got_elt), len(exp_elt))
                return False
            for idx, child in enumerate(got_elt):
                if not equalElt(child, exp_elt[idx]):
                    return False
            return True

        def remove_blank(xml):
            lines = [line.strip() for line in re.sub(r'[ \t\r\f\v]+', ' ', xml).split('\n')]
            return '\n'.join([line for line in lines if line])

        xml_elt = etree.fromstring(remove_blank(xml) if ignore_blank else xml)
        expected_elt = etree.fromstring(remove_blank(expected) if ignore_blank else expected)

        if not equalElt(xml_elt, expected_elt):
            print "---"
            print "XML are not equals:"
            print "got:\n-\n%s\n-\n\n" % etree.tostring(xml_elt, encoding='utf-8')
            print "was expecting:\n-\n%s\n-\n\n" % etree.tostring(expected_elt, encoding='utf-8')
            print "---"
            raise DifferentXMLException

    def assertEqualUnsortedList(self, a, b, msg):
        counter_a = Counter(a)
        counter_b = Counter(b)
        if counter_a != counter_b:
            print "---"
            print "Unsorted lists are not equals:"
            print "got          : %s" % counter_a
            print "was expecting: %s" % counter_b
            if msg:
                print msg
            print "---"
            raise DifferentListException
