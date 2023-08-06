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

""" Plugin XEP-0277 tests """

from sat.test import helpers
from sat.plugins import plugin_xep_0277
from sat.plugins import plugin_misc_text_syntaxes
from sat.tools.xml_tools import ElementParser
import re


class XEP_0277Test(helpers.SatTestCase):

    PUBSUB_ENTRY_1 = """
    <item id="c745a688-9b02-11e3-a1a3-c0143dd4fe51" xmlns="%s">
        <entry>
            <title type="text">&lt;span&gt;titre&lt;/span&gt;</title>
            <id>c745a688-9b02-11e3-a1a3-c0143dd4fe51</id>
            <updated>2014-02-21T16:16:39+02:00</updated>
            <published>2014-02-21T16:16:38+02:00</published>
            <content type="text">&lt;p&gt;contenu&lt;/p&gt;texte sans balise&lt;p&gt;autre contenu&lt;/p&gt;</content>
            <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml"><p>contenu</p>texte sans balise<p>autre contenu</p></div></content>
        <author>
            <name>test1@souliane.org</name>
        </author>
    </entry>
    </item>
    """ % plugin_xep_0277.NS_PUBSUB

    PUBSUB_ENTRY_2 = """
    <item id="c745a688-9b02-11e3-a1a3-c0143dd4fe51" xmlns="%s">
        <entry xmlns=''>
            <title type="text">&lt;div&gt;titre&lt;/div&gt;</title>
            <title type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml"><div style="background-image: url('xxx');">titre</div></div></title>
            <id>c745a688-9b02-11e3-a1a3-c0143dd4fe51</id>
            <updated>2014-02-21T16:16:39+02:00</updated>
            <published>2014-02-21T16:16:38+02:00</published>
            <content type="text">&lt;div&gt;&lt;p&gt;contenu&lt;/p&gt;texte dans balise&lt;p&gt;autre contenu&lt;/p&gt;&lt;/div&gt;</content>
            <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml"><div><p>contenu</p>texte dans balise<p>autre contenu</p></div></div></content>
        <author>
            <nick>test1@souliane.org</nick>
        </author>
    </entry>
    </item>
    """ % plugin_xep_0277.NS_PUBSUB

    def setUp(self):
        self.host = helpers.FakeSAT()

        class XEP_0163(object):
            def __init__(self, host):
                pass

            def addPEPEvent(self, *args):
                pass
        self.host.plugins["XEP-0163"] = XEP_0163(self.host)
        self.host.plugins["TEXT-SYNTAXES"] = plugin_misc_text_syntaxes.TextSyntaxes(self.host)
        self.plugin = plugin_xep_0277.XEP_0277(self.host)

    def test_item2mbdata_1(self):
        expected = {'id': 'c745a688-9b02-11e3-a1a3-c0143dd4fe51',
                    'title': '<span>titre</span>',
                    'updated': '1392992199.0',
                    'published': '1392992198.0',
                    'content': '<p>contenu</p>texte sans balise<p>autre contenu</p>',
                    'content_xhtml': '<div><p>contenu</p>texte sans balise<p>autre contenu</p></div>',
                    'author': 'test1@souliane.org'
                    }
        d = self.plugin.item2mbdata(ElementParser()(self.PUBSUB_ENTRY_1))
        d.addCallback(self.assertEqual, expected)
        return d

    def test_item2mbdata_2(self):
        expected = {'id': 'c745a688-9b02-11e3-a1a3-c0143dd4fe51',
                    'title': '<div>titre</div>',
                    'title_xhtml': '<div style="">titre</div>',
                    'updated': '1392992199.0',
                    'published': '1392992198.0',
                    'content': '<div><p>contenu</p>texte dans balise<p>autre contenu</p></div>',
                    'content_xhtml': '<div><p>contenu</p>texte dans balise<p>autre contenu</p></div>',
                    'author': 'test1@souliane.org'
                    }
        d = self.plugin.item2mbdata(ElementParser()(self.PUBSUB_ENTRY_2))
        d.addCallback(self.assertEqual, expected)
        return d
