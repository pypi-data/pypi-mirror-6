#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for Publish-Subscribe (xep-0071)
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
from logging import debug, info, error

from wokkel import disco, pubsub, iwokkel
from zope.interface import implements
# from lxml import etree
from lxml import html
try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

NS_XHTML_IM = 'http://jabber.org/protocol/xhtml-im'
NS_XHTML = 'http://www.w3.org/1999/xhtml'

PLUGIN_INFO = {
    "name": "XHTML-IM Plugin",
    "import_name": "XEP-0071",
    "type": "XEP",
    "protocols": ["XEP-0071"],
    "dependencies": ["TEXT-SYNTAXES"],
    "main": "XEP_0071",
    "handler": "yes",
    "description": _("""Implementation of XHTML-IM""")
}

allowed = {
          "a": set(["href", "style", "type"]),
          "blockquote": set(["style"]),
          "body": set(["style"]),
          "br": set([]),
          "cite": set(["style"]),
          "em": set([]),
          "img": set(["alt", "height", "src", "style", "width"]),
          "li": set(["style"]),
          "ol": set(["style"]),
          "p": set(["style"]),
          "span": set(["style"]),
          "strong": set([]),
          "ul": set(["style"]),
          }

styles_allowed = ["background-color", "color", "font-family", "font-size", "font-style", "font-weight", "margin-left", "margin-right", "text-align", "text-decoration"]

blacklist = ['script'] # tag that we have to kill (we don't keep content)


class XEP_0071(object):
    SYNTAX_XHTML_IM = "XHTML-IM"

    def __init__(self, host):
        info(_("XHTML-IM plugin initialization"))
        self.host = host
        self.synt_plg = self.host.plugins["TEXT-SYNTAXES"]
        self.synt_plg.addSyntax(self.SYNTAX_XHTML_IM, lambda xhtml: xhtml, self.XHTML2XHTML_IM, [self.synt_plg.OPT_HIDDEN])
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)
        host.trigger.add("sendMessage", self.sendMessageTrigger)

    def getHandler(self, profile):
        return XEP_0071_handler(self)

    def _messagePostTreat(self, data, body_elt):
        """ Callback which manage the post treatment of the message in case of XHTML-IM found
        @param data: data send by MessageReceived trigger through post_treat deferred
        @param xhtml_im: XHTML-IM body element found
        @return: the data with the extra parameter updated
        """
        #TODO: check if text only body is empty, then try to convert XHTML-IM to pure text and show a warning message
        def converted(xhtml):
            data['extra']['xhtml'] = xhtml
            return data
        d = self.synt_plg.convert(body_elt.toXml(), self.SYNTAX_XHTML_IM, safe=True)
        d.addCallback(converted)
        return d

    def _sendMessageAddRich(self, mess_data, profile):
        """ Construct XHTML-IM node and add it XML element
        @param mess_data: message data as sended by sendMessage callback
        """
        def syntax_converted(xhtml_im):
            message_elt = mess_data['xml']
            html_elt = message_elt.addElement('html', NS_XHTML_IM)
            body_elt = html_elt.addElement('body', NS_XHTML)
            body_elt.addRawXml(xhtml_im)
            mess_data['extra']['xhtml'] = xhtml_im
            return mess_data

        syntax = self.synt_plg.getCurrentSyntax(profile)
        rich = mess_data['extra'].get('rich', '')
        xhtml = mess_data['extra'].get('xhtml', '')
        if rich:
            d = self.synt_plg.convert(rich, syntax, self.SYNTAX_XHTML_IM)
            if xhtml:
                raise exceptions.DataError(_("Can't have xhtml and rich content at the same time"))
        if xhtml:
            d = self.synt_plg.clean_xhtml(xhtml)
        d.addCallback(syntax_converted)
        return d

    def messageReceivedTrigger(self, message, post_treat, profile):
        """ Check presence of XHTML-IM in message
        """
        try:
            html_elt = message.elements(NS_XHTML_IM, 'html').next()
            body_elt = html_elt.elements(NS_XHTML, 'body').next()
            # OK, we have found rich text
            post_treat.addCallback(self._messagePostTreat, body_elt)
        except StopIteration:
            # No XHTML-IM
            pass
        return True

    def sendMessageTrigger(self, mess_data, treatments, profile):
        """ Check presence of rich text in extra
        """
        if 'rich' in mess_data['extra'] or 'xhtml' in mess_data['extra']:
            treatments.addCallback(self._sendMessageAddRich, profile)
        return True

    def _purgeStyle(self, styles_raw):
        """ Remove unauthorised styles according to the XEP-0071
        @param styles_raw: raw styles (value of the style attribute)
        """
        purged = []

        styles = [style.strip().split(':') for style in styles_raw.split(';')]

        for style_tuple in styles:
            if len(style_tuple) != 2:
                continue
            name, value = style_tuple
            name = name.strip()
            if name not in styles_allowed:
                continue
            purged.append((name, value.strip()))

        return u'; '.join([u"%s: %s" % data for data in purged])

    def XHTML2XHTML_IM(self, xhtml):
        """ Convert XHTML document to XHTML_IM subset
        @param xhtml: raw xhtml to convert
        """
        # TODO: more clever tag replacement (replace forbidden tags with equivalents when possible)

        parser = html.HTMLParser(remove_comments=True, encoding='utf-8')
        root = html.fromstring(xhtml, parser=parser)
        body_elt = root.find('body')
        if body_elt is None:
            # we use the whole XML as body if no body element is found
            body_elt = html.Element('body')
            body_elt.append(root)
        else:
            body_elt.attrib.clear()

        allowed_tags = allowed.keys()
        to_strip = []
        for elem in body_elt.iter():
            if elem.tag not in allowed_tags:
                to_strip.append(elem)
            else:
                # we remove unallowed attributes
                attrib = elem.attrib
                att_to_remove = set(attrib).difference(allowed[elem.tag])
                for att in att_to_remove:
                    del(attrib[att])
                if "style" in attrib:
                    attrib["style"] = self._purgeStyle(attrib["style"])

        for elem in to_strip:
            if elem.tag in blacklist:
                #we need to remove the element and all descendants
                debug(u"removing black listed tag: %s" % (elem.tag))
                elem.drop_tree()
            else:
                elem.drop_tag()
        if len(body_elt) !=1:
            root_elt = body_elt
            body_elt.tag = "p"
        else:
            root_elt = body_elt[0]

        return html.tostring(root_elt, encoding='unicode', method='xml')

class XEP_0071_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_XHTML_IM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
