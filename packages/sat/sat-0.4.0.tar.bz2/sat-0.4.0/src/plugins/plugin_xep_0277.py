#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for microblogging over XMPP (xep-0277)
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
from logging import debug, info, warning, error
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from sat.core import exceptions
from sat.tools.xml_tools import ElementParser

from wokkel import pubsub
from feed import atom, date
from lxml import etree
import uuid
from time import time
import urlparse
from cgi import escape

NS_MICROBLOG = 'urn:xmpp:microblog:0'
NS_XHTML = 'http://www.w3.org/1999/xhtml'
NS_PUBSUB = 'http://jabber.org/protocol/pubsub'

PLUGIN_INFO = {
    "name": "Microblogging over XMPP Plugin",
    "import_name": "XEP-0277",
    "type": "XEP",
    "protocols": [],
    "dependencies": ["XEP-0163", "XEP-0060", "TEXT-SYNTAXES"],
    "main": "XEP_0277",
    "handler": "no",
    "description": _("""Implementation of microblogging Protocol""")
}


class NodeAccessChangeException(Exception):
    pass


class XEP_0277(object):

    def __init__(self, host):
        info(_("Microblogging plugin initialization"))
        self.host = host
        self.host.plugins["XEP-0163"].addPEPEvent("MICROBLOG", NS_MICROBLOG, self.microblogCB, self.sendMicroblog)
        host.bridge.addMethod("getLastMicroblogs", ".plugin",
                              in_sign='sis', out_sign='aa{ss}',
                              method=self.getLastMicroblogs,
                              async=True,
                              doc={'summary': 'retrieve items',
                                   'param_0': 'jid: publisher of wanted microblog',
                                   'param_1': 'max_items: see XEP-0060 #6.5.7',
                                   'param_2': '%(doc_profile)s',
                                   'return': 'list of microblog data (dict)'})
        host.bridge.addMethod("setMicroblogAccess", ".plugin", in_sign='ss', out_sign='',
                              method=self.setMicroblogAccess,
                              async=True,
                              doc={})

    def parseCommentUrl(self, node_url):
        """Determine the fields comments_service and comments_node of a microblog data
        from the href attribute of an entry's link element. For example this input:
        xmpp:sat-pubsub.libervia.org?node=urn%3Axmpp%3Acomments%3A_c5c4a142-2279-4b2a-ba4c-1bc33aa87634__urn%3Axmpp%3Agroupblog%3Asouliane%libervia.org
        will return (JID(u'sat-pubsub.libervia.org'), 'urn:xmpp:comments:_c5c4a142-2279-4b2a-ba4c-1bc33aa87634__urn:xmpp:groupblog:souliane%libervia.org')
        @return: a tuple (JID, str)
        """
        parsed_url = urlparse.urlparse(node_url, 'xmpp')
        service = jid.JID(parsed_url.path)
        queries = parsed_url.query.split(';')
        parsed_queries = dict()
        for query in queries:
            parsed_queries.update(urlparse.parse_qs(query))
        node = parsed_queries.get('node', [''])[0]

        if not node:
            raise exceptions.DataError('Invalid comments link')

        return (service, node)

    def __removeXHTMLMarkups(self, xhtml):
        """
        Remove XHTML markups from the given string.
        @param xhtml: the XHTML string to be cleaned
        @return: a Deferred instance for the cleaned string
        """
        return self.host.plugins["TEXT-SYNTAXES"].convert(xhtml,
                                                          self.host.plugins["TEXT-SYNTAXES"].SYNTAX_XHTML,
                                                          self.host.plugins["TEXT-SYNTAXES"].SYNTAX_TEXT,
                                                          False)

    @defer.inlineCallbacks
    def item2mbdata(self, item):
        """Convert an XML Item to microblog data used in bridge API
        @param item: domish.Element of microblog item
        @return: microblog data (dictionary)"""

        def xpath(elt, path):
            """Return the XPATH result of an entry element or its descendance, works with both:
            - no namespace, that means it is inherited from the parent item node --> NS_PUBSUB
            - empty namespace
            XXX: check why the received entries have no namespace when they are retrieved
            from self.host.plugins["XEP-0060"].getItems and they have an empty namespace
            when they are received with an event.
            """
            result = elt.xpath(path)
            if len(result) > 0:
                return result
            return elt.xpath('/'.join(['ns:%s' % tag for tag in path.split('/')]), namespaces={'ns': NS_PUBSUB})

        # convert a date string to float without dealing with the date format
        date2float = lambda elt, path: unicode(date.rfc3339.tf_from_timestamp(xpath(elt, path)[0].text))

        item_elt = etree.fromstring(item.toXml().encode('utf-8'))
        try:
            entry_elt = xpath(item_elt, 'entry')[0]
        except IndexError:
            raise exceptions.DataError(_('No entry found in the pubsub item %s') % item_elt.get('id', ''))

        microblog_data = {}

        for key in ['title', 'content']:  # process the textual elements
            for attr_elt in xpath(entry_elt, key):
                attr_content = self.__getLXMLInnerContent(attr_elt)
                if not attr_content.strip():
                    continue  # element with empty value
                content_type = attr_elt.get('type', 'text').lower()
                if content_type == 'xhtml':
                    text = self.__decapsulateExtraNS(attr_content)
                    microblog_data['%s_xhtml' % key] = yield self.host.plugins["TEXT-SYNTAXES"].clean_xhtml(text)
                else:
                    microblog_data[key] = attr_content
            if key not in microblog_data and ('%s_xhtml' % key) in microblog_data:
                microblog_data[key] = yield self.__removeXHTMLMarkups(microblog_data['%s_xhtml' % key])

        try:  # check for mandatory elements
            microblog_data['id'] = xpath(entry_elt, 'id')[0].text
            microblog_data['updated'] = date2float(entry_elt, 'updated')
            assert('title' in microblog_data)  # has been processed already
        except IndexError:
            error(_("Atom entry %s misses a required element") % item_elt.get('id', ''))
            raise exceptions.DataError

        if 'content' not in microblog_data:  # use the atom title data as the microblog body content
            microblog_data['content'] = microblog_data['title']
            del microblog_data['title']
            if 'title_xhtml' in microblog_data:
                microblog_data['content_xhtml'] = microblog_data['title_xhtml']
                del microblog_data['title_xhtml']

        # recommended and optional elements with a fallback value
        try:
            microblog_data['published'] = date2float(entry_elt, 'published')
        except IndexError:
            microblog_data['published'] = microblog_data['updated']

        # other recommended and optional elements
        try:
            link_elt = xpath(entry_elt, "link")[0]
            try:
                assert(link_elt.attrib['title'] == "comments")
                microblog_data['comments'] = link_elt.attrib['href']
                service, node = self.parseCommentUrl(microblog_data["comments"])
                microblog_data['comments_service'] = service.full()
                microblog_data['comments_node'] = node
            except (exceptions.DataError, RuntimeError, KeyError):
                warning(_("Can't parse the link element of pubsub entry %s") % microblog_data['id'])
        except:
            pass
        try:
            microblog_data['author'] = xpath(entry_elt, 'author/name')[0].text
        except IndexError:
            try:  # XXX: workaround for Jappix behaviour
                microblog_data['author'] = xpath(entry_elt, 'author/nick')[0].text
            except IndexError:
                warning(_("Can't find author element in pubsub entry %s") % microblog_data['id'])

        defer.returnValue(microblog_data)

    def __getLXMLInnerContent(self, elt):
        """Return the inner content of a lxml.etree.Element. It is not
        trivial because the lxml tostring method would return the full
        content including elt's tag and attributes, and elt.getchildren()
        would skip a text value which is not within an element..."""
        return self.__getDomishInnerContent(ElementParser()(etree.tostring(elt)))

    def __getDomishInnerContent(self, elt):
        """Return the inner content of a domish.Element."""
        result = ''
        for child in elt.children:
            try:
                result += child.toXml()  # child id a domish.Element
            except AttributeError:
                result += child  # child is unicode
        return result

    def __decapsulateExtraNS(self, text):
        """Check for XHTML namespace and decapsulate the content so the user
        who wants to modify an entry will see the text that he entered. Also
        this avoids successive encapsulation with a new <div>...</div> at
        each modification (encapsulation is done in self.data2entry)"""
        elt = ElementParser()(text)
        if elt.uri != NS_XHTML:
            raise exceptions.DataError(_('Content of type XHTML must declare its namespace!'))
        return self.__getDomishInnerContent(elt)

    def microblogCB(self, itemsEvent, profile):
        d = defer.Deferred()

        def manageItem(microblog_data):
            self.host.bridge.personalEvent(itemsEvent.sender.full(), "MICROBLOG", microblog_data, profile)

        for item in itemsEvent.items:
            d.addCallback(lambda ignore: self.item2mbdata(item))
            d.addCallback(manageItem)

        d.callback(None)
        return d

    @defer.inlineCallbacks
    def data2entry(self, data, profile):
        """Convert a data dict to en entry usable to create an item
        @param data: data dict as given by bridge method.
        @return: deferred which fire domish.Element"""
        _uuid = unicode(uuid.uuid1())
        _entry = atom.Entry()
        _entry.title = ''  # reset the default value which is not empty

        elems = {'title': atom.Title, 'content': atom.Content}
        synt = self.host.plugins["TEXT-SYNTAXES"]

        # loop on ('title', 'title_rich', 'title_xhtml', 'content', 'content_rich', 'content_xhtml')
        for key in elems.keys():
            for type_ in ['', 'rich', 'xhtml']:
                attr = "%s_%s" % (key, type_) if type_ else key
                if attr in data:
                    if type_:
                        if type_ == 'rich':  # convert input from current syntax to XHTML
                            converted = yield synt.convert(data[attr], synt.getCurrentSyntax(profile), "XHTML")
                        else:  # clean the XHTML input
                            converted = yield synt.clean_xhtml(data[attr])
                        elem = elems[key]((u'<div xmlns="%s">%s</div>' % (NS_XHTML, converted)).encode('utf-8'))
                        elem.attrs['type'] = 'xhtml'
                        if hasattr(_entry, '%s_xhtml' % key):
                            raise exceptions.DataError(_("Can't have xhtml and rich content at the same time"))
                        setattr(_entry, '%s_xhtml' % key, elem)
                    else:  # raw text only needs to be escaped to get HTML-safe sequence
                        elem = elems[key](escape(data[attr]).encode('utf-8'))
                        elem.attrs['type'] = 'text'
                        setattr(_entry, key, elem)
            if not getattr(_entry, key).text:
                if hasattr(_entry, '%s_xhtml' % key):
                    text = yield self.__removeXHTMLMarkups(getattr(_entry, '%s_xhtml' % key).text)
                    setattr(_entry, key, text)
        if not _entry.title.text:  # eventually move the data from content to title
            _entry.title = _entry.content.text
            _entry.title.attrs['type'] = _entry.content.attrs['type']
            _entry.content.text = ''
            _entry.content.attrs['type'] = ''
            if hasattr(_entry, 'content_xhtml'):
                _entry.title_xhtml = atom.Title(_entry.content_xhtml.text)
                _entry.title_xhtml.attrs['type'] = _entry.content_xhtml.attrs['type']
                _entry.content_xhtml.text = ''
                _entry.content_xhtml.attrs['type'] = ''

        _entry.author = atom.Author()
        _entry.author.name = data.get('author', self.host.getJidNStream(profile)[0].userhost()).encode('utf-8')
        _entry.updated = float(data.get('updated', time()))
        _entry.published = float(data.get('published', time()))
        entry_id = data.get('id', unicode(_uuid))
        _entry.id = entry_id.encode('utf-8')
        if 'comments' in data:
            link = atom.Link()
            link.attrs['href'] = data['comments']
            link.attrs['rel'] = 'replies'
            link.attrs['title'] = 'comments'
            _entry.links.append(link)
        _entry_elt = ElementParser()(str(_entry).decode('utf-8'))
        item = pubsub.Item(id=entry_id, payload=_entry_elt)
        defer.returnValue(item)

    @defer.inlineCallbacks
    def sendMicroblog(self, data, profile):
        """Send XEP-0277's microblog data
        @param data: must include content
        @param profile: profile which send the mood"""
        if 'content' not in data:
            error(_("Microblog data must contain at least 'content' key"))
            raise exceptions.DataError('no "content" key found')
        content = data['content']
        if not content:
            error(_("Microblog data's content value must not be empty"))
            raise exceptions.DataError('empty content')
        item = yield self.data2entry(data, profile)
        ret = yield self.host.plugins["XEP-0060"].publish(None, NS_MICROBLOG, [item], profile_key=profile)
        defer.returnValue(ret)

    def getLastMicroblogs(self, pub_jid, max_items=10, profile_key='@DEFAULT@'):
        """Get the last published microblogs
        @param pub_jid: jid of the publisher
        @param max_items: how many microblogs we want to get
        @param profile_key: profile key
        """
        def resultToArray(result):
            ret = []
            for (success, value) in result:
                if success:
                    ret.append(value)
                else:
                    error('Error while getting last microblog')
            return ret

        d = self.host.plugins["XEP-0060"].getItems(jid.JID(pub_jid), NS_MICROBLOG, max_items=max_items, profile_key=profile_key)
        d.addCallback(lambda items: defer.DeferredList(map(self.item2mbdata, items)))
        d.addCallback(resultToArray)
        return d

    def setMicroblogAccess(self, access="presence", profile_key='@DEFAULT@'):
        """Create a microblog node on PEP with given access
        If the node already exists, it change options
        @param access: Node access model, according to xep-0060 #4.5
        @param profile_key: profile key"""

        _jid, xmlstream = self.host.getJidNStream(profile_key)
        if not _jid:
            error(_("Can't find profile's jid"))
            return
        C = self.host.plugins["XEP-0060"]
        _options = {C.OPT_ACCESS_MODEL: access, C.OPT_PERSIST_ITEMS: 1, C.OPT_MAX_ITEMS: -1, C.OPT_DELIVER_PAYLOADS: 1, C.OPT_SEND_ITEM_SUBSCRIBE: 1}

        def cb(result):
            #Node is created with right permission
            debug(_("Microblog node has now access %s") % access)

        def fatal_err(s_error):
            #Something went wrong
            error(_("Can't set microblog access"))
            raise NodeAccessChangeException()

        def err_cb(s_error):
            #If the node already exists, the condition is "conflict",
            #else we have an unmanaged error
            if s_error.value.condition == 'conflict':
                #d = self.host.plugins["XEP-0060"].deleteNode(_jid.userhostJID(), NS_MICROBLOG, profile_key=profile_key)
                #d.addCallback(lambda x: create_node().addCallback(cb).addErrback(fatal_err))
                change_node_options().addCallback(cb).addErrback(fatal_err)
            else:
                fatal_err(s_error)

        def create_node():
            return self.host.plugins["XEP-0060"].createNode(_jid.userhostJID(), NS_MICROBLOG, _options, profile_key=profile_key)

        def change_node_options():
            return self.host.plugins["XEP-0060"].setOptions(_jid.userhostJID(), NS_MICROBLOG, _jid.userhostJID(), _options, profile_key=profile_key)

        create_node().addCallback(cb).addErrback(err_cb)
