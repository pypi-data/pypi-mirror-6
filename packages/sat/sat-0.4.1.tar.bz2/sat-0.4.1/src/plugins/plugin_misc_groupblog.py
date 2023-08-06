#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for microbloging with roster access
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
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.xish.domish import Element
from sat.core import exceptions
from wokkel import disco, data_form, iwokkel
from zope.interface import implements
from feed import date
import uuid
import urllib

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

NS_PUBSUB = 'http://jabber.org/protocol/pubsub'
NS_GROUPBLOG = 'http://goffi.org/protocol/groupblog'
NS_NODE_PREFIX = 'urn:xmpp:groupblog:'
NS_COMMENT_PREFIX = 'urn:xmpp:comments:'
#NS_PUBSUB_EXP = 'http://goffi.org/protocol/pubsub' #for non official features
NS_PUBSUB_EXP = NS_PUBSUB  # XXX: we can't use custom namespace as Wokkel's PubSubService use official NS
NS_PUBSUB_ITEM_ACCESS = NS_PUBSUB_EXP + "#item-access"
NS_PUBSUB_CREATOR_JID_CHECK = NS_PUBSUB_EXP + "#creator-jid-check"
NS_PUBSUB_ITEM_CONFIG = NS_PUBSUB_EXP + "#item-config"
NS_PUBSUB_AUTO_CREATE = NS_PUBSUB + "#auto-create"
TYPE_COLLECTION = 'collection'
ACCESS_TYPE_MAP = { 'PUBLIC': 'open',
                    'GROUP': 'roster',
                    'JID': None, #JID is not yet managed
                  }

PLUGIN_INFO = {
    "name": "Group blogging throught collections",
    "import_name": "groupblog",
    "type": "MISC",
    "protocols": [],
    "dependencies": ["XEP-0277"],
    "main": "GroupBlog",
    "handler": "yes",
    "description": _("""Implementation of microblogging with roster access""")
}


class NoCompatiblePubSubServerFound(Exception):
    pass


class BadAccessTypeError(Exception):
    pass


class BadAccessListError(Exception):
    pass


class UnknownType(Exception):
    pass


class GroupBlog(object):
    """This class use a SàT PubSub Service to manage access on microblog"""

    def __init__(self, host):
        info(_("Group blog plugin initialization"))
        self.host = host

        host.bridge.addMethod("sendGroupBlog", ".plugin", in_sign='sassa{ss}s', out_sign='',
                              method=self.sendGroupBlog,
                              async=True)

        host.bridge.addMethod("deleteGroupBlog", ".plugin", in_sign='(sss)ss', out_sign='',
                              method=self.deleteGroupBlog,
                              async=True)

        host.bridge.addMethod("updateGroupBlog", ".plugin", in_sign='(sss)ssa{ss}s', out_sign='',
                              method=self.updateGroupBlog,
                              async=True)

        host.bridge.addMethod("sendGroupBlogComment", ".plugin", in_sign='ssa{ss}s', out_sign='',
                              method=self.sendGroupBlogComment,
                              async=True)

        host.bridge.addMethod("getLastGroupBlogs", ".plugin",
                              in_sign='sis', out_sign='aa{ss}',
                              method=self.getLastGroupBlogs,
                              async=True)

        host.bridge.addMethod("getLastGroupBlogsAtom", ".plugin",
                              in_sign='sis', out_sign='s',
                              method=self.getLastGroupBlogsAtom,
                              async=True)

        host.bridge.addMethod("getMassiveLastGroupBlogs", ".plugin",
                              in_sign='sasis', out_sign='a{saa{ss}}',
                              method=self._getMassiveLastGroupBlogs,
                              async=True)

        host.bridge.addMethod("getGroupBlogComments", ".plugin",
                              in_sign='sss', out_sign='aa{ss}',
                              method=self.getGroupBlogComments,
                              async=True)

        host.bridge.addMethod("subscribeGroupBlog", ".plugin", in_sign='ss', out_sign='',
                              method=self.subscribeGroupBlog,
                              async=True)

        host.bridge.addMethod("massiveSubscribeGroupBlogs", ".plugin", in_sign='sass', out_sign='',
                              method=self._massiveSubscribeGroupBlogs,
                              async=True)

        host.trigger.add("PubSubItemsReceived", self.pubSubItemsReceivedTrigger)

    def getHandler(self, profile):
        return GroupBlog_handler()

    @defer.inlineCallbacks
    def _initialise(self, profile_key):
        """Check that the data for this profile are initialised, and do it else
        @param profile_key: %(doc_profile)s"""
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileUnknownError

        client = self.host.getClient(profile)
        if not client:
            error(_('No client for this profile key: %s') % profile_key)
            raise Exception("Unknown profile")
        yield client.client_initialized  # we want to be sure that the client is initialized

        #we first check that we have a item-access pubsub server
        if not hasattr(client, "item_access_pubsub"):
            debug(_('Looking for item-access power pubsub server'))
            #we don't have any pubsub server featuring item access yet
            client.item_access_pubsub = None
            client._item_access_pubsub_pending = defer.Deferred()
            for entity in self.host.memory.getServerServiceEntities("pubsub", "service", profile=profile):
                _disco = yield client.disco.requestInfo(entity)
                #if set([NS_PUBSUB_ITEM_ACCESS, NS_PUBSUB_AUTO_CREATE, NS_PUBSUB_CREATOR_JID_CHECK]).issubset(_disco.features):
                if set([NS_PUBSUB_AUTO_CREATE, NS_PUBSUB_CREATOR_JID_CHECK]).issubset(_disco.features):
                    info(_("item-access powered pubsub service found: [%s]") % entity.full())
                    client.item_access_pubsub = entity
            client._item_access_pubsub_pending.callback(None)

        if hasattr(client, "_item_access_pubsub_pending"):
            #XXX: we need to wait for item access pubsub service check
            yield client._item_access_pubsub_pending
            del client._item_access_pubsub_pending

        if not client.item_access_pubsub:
            error(_("No item-access powered pubsub server found, can't use group blog"))
            raise NoCompatiblePubSubServerFound

        defer.returnValue((profile, client))

    def pubSubItemsReceivedTrigger(self, event, profile):
        """"Trigger which catch groupblogs events"""

        if event.nodeIdentifier.startswith(NS_NODE_PREFIX):
            # Microblog
            publisher = jid.JID(event.nodeIdentifier[len(NS_NODE_PREFIX):])
            origin_host = publisher.host.split('.')
            event_host = event.sender.host.split('.')
            #FIXME: basic origin check, must be improved
            #TODO: automatic security test
            if (not (origin_host)
                    or len(event_host) < len(origin_host)
                    or event_host[-len(origin_host):] != origin_host):
                warning("Host incoherence between %s and %s (hack attempt ?)" % (unicode(event.sender),
                                                                                 unicode(publisher)))
                return False

            client = self.host.getClient(profile)

            def gbdataManagementMicroblog(gbdata):
                for gbdatum in gbdata:
                    self.host.bridge.personalEvent(publisher.full(), "MICROBLOG", gbdatum, profile)

            d = self._itemsConstruction(event.items, publisher, client)
            d.addCallback(gbdataManagementMicroblog)
            return False

        elif event.nodeIdentifier.startswith(NS_COMMENT_PREFIX):
            # Comment
            def gbdataManagementComments(gbdata):
                for gbdatum in gbdata:
                    publisher = None # FIXME: see below (_handleCommentsItems)
                    self.host.bridge.personalEvent(publisher.full() if publisher else gbdatum["author"], "MICROBLOG", gbdatum, profile)
            d = self._handleCommentsItems(event.items, event.sender, event.nodeIdentifier)
            d.addCallback(gbdataManagementComments)
            return False
        return True

    @defer.inlineCallbacks
    def _handleCommentsItems(self, items, service, node_identifier):
        """ Convert comments items to groupblog data, and send them as signals
        @param items: comments items
        @param service: jid of the PubSub service used
        @param node_identifier: comments node
        @return: list of group blog data
        """
        ret = []
        for item in items:
            publisher = "" # FIXME: publisher attribute for item in SàT pubsub is not managed yet, so
                           #        publisher is not checked and can be easily spoofed. This need to be fixed
                           #        quickly.
            microblog_data = yield self.item2gbdata(item, "comment")
            microblog_data["service"] = service.userhost()
            microblog_data["node"] = node_identifier
            microblog_data["verified_publisher"] = "true" if publisher else "false"
            ret.append(microblog_data)
        defer.returnValue(ret)

    def _parseAccessData(self, microblog_data, item):
        P = self.host.plugins["XEP-0060"]
        form_elts = [child for child in item.elements() if child.name == "x"]
        for form_elt in form_elts:
            form = data_form.Form.fromElement(form_elt)

            if (form.formNamespace == NS_PUBSUB_ITEM_CONFIG):
                access_model = form.get(P.OPT_ACCESS_MODEL, 'open')
                if access_model == "roster":
                    try:
                        microblog_data["groups"] = '\n'.join(form.fields[P.OPT_ROSTER_GROUPS_ALLOWED].values)
                    except KeyError:
                        warning("No group found for roster access-model")
                        microblog_data["groups"] = ''

                break

    @defer.inlineCallbacks
    def item2gbdata(self, item, _type="main_item"):
        """ Convert item to microblog data dictionary + add access data """
        microblog_data = yield self.host.plugins["XEP-0277"].item2mbdata(item)
        microblog_data["type"] = _type
        self._parseAccessData(microblog_data, item)
        defer.returnValue(microblog_data)

    def getNodeName(self, publisher):
        """Retrieve the name of publisher's node
        @param publisher: publisher's jid
        @return: node's name (string)"""
        return NS_NODE_PREFIX + publisher.userhost()

    def _publishMblog(self, service, client, access_type, access_list, message, extra):
        """Actually publish the message on the group blog
        @param service: jid of the item-access pubsub service
        @param client: SatXMPPClient of the publisher
        @param access_type: one of "PUBLIC", "GROUP", "JID"
        @param access_list: set of entities (empty list for all, groups or jids) allowed to see the item
        @param message: message to publish
        @param extra: dict which option name as key, which can be:
            - allow_comments: True to accept comments, False else (default: False)
            - rich: if present, contain rich text in currently selected syntax
        """
        node_name = self.getNodeName(client.jid)
        mblog_data = {'content': message}

        for attr in ['content_rich', 'title', 'title_rich']:
            if attr in extra and extra[attr]:
                mblog_data[attr] = extra[attr]
        P = self.host.plugins["XEP-0060"]
        access_model_value = ACCESS_TYPE_MAP[access_type]

        if extra.get('allow_comments', 'False').lower() == 'true':
            # XXX: use the item identifier? http://bugs.goffi.org/show_bug.cgi?id=63
            comments_node = self.__fillCommentsElement(mblog_data, None, node_name, service)
            _options = {P.OPT_ACCESS_MODEL: access_model_value,
                        P.OPT_PERSIST_ITEMS: 1,
                        P.OPT_MAX_ITEMS: -1,
                        P.OPT_DELIVER_PAYLOADS: 1,
                        P.OPT_SEND_ITEM_SUBSCRIBE: 1,
                        P.OPT_PUBLISH_MODEL: "subscribers",  # TODO: should be open if *both* node and item access_model are open (public node and item)
                       }
            if access_model_value == 'roster':
                _options[P.OPT_ROSTER_GROUPS_ALLOWED] = list(access_list)

            # FIXME: check comments node creation success, at the moment this is a potential security risk (if the node
            #        already exists, the creation will silently fail, but the comments link will stay the same, linking to a
            #        node owned by somebody else)
            defer_blog = self.host.plugins["XEP-0060"].createNode(service, comments_node, _options, profile_key=client.profile)

        def itemCreated(mblog_item):
            form = data_form.Form('submit', formNamespace=NS_PUBSUB_ITEM_CONFIG)

            if access_type == "PUBLIC":
                if access_list:
                    raise BadAccessListError("access_list must be empty for PUBLIC access")
                access = data_form.Field(None, P.OPT_ACCESS_MODEL, value=access_model_value)
                form.addField(access)
            elif access_type == "GROUP":
                access = data_form.Field(None, P.OPT_ACCESS_MODEL, value=access_model_value)
                allowed = data_form.Field(None, P.OPT_ROSTER_GROUPS_ALLOWED, values=access_list)
                form.addField(access)
                form.addField(allowed)
                mblog_item.addChild(form.toElement())
            elif access_type == "JID":
                raise NotImplementedError
            else:
                error(_("Unknown access_type"))
                raise BadAccessTypeError

            defer_blog = self.host.plugins["XEP-0060"].publish(service, node_name, items=[mblog_item], profile_key=client.profile)
            defer_blog.addErrback(self._mblogPublicationFailed)
            return defer_blog

        entry_d = self.host.plugins["XEP-0277"].data2entry(mblog_data, client.profile)
        entry_d.addCallback(itemCreated)
        return entry_d

    def __fillCommentsElement(self, mblog_data, entry_id, node_name, service_jid):
        """
        @param mblog_data: dict containing the microblog data
        @param entry_id: unique identifier of the entry
        @param node_name: the pubsub node name
        @param service_jid: the JID of the pubsub service
        @return: the comments node string
        """
        if entry_id is None:
            entry_id = unicode(uuid.uuid4())
        comments_node = "%s_%s__%s" % (NS_COMMENT_PREFIX, entry_id, node_name)
        mblog_data['comments'] = "xmpp:%(service)s?%(query)s" % {'service': service_jid.userhost(),
                                                                 'query': urllib.urlencode([('node', comments_node.encode('utf-8'))])}
        return comments_node

    def _mblogPublicationFailed(self, failure):
        #TODO
        return failure

    def sendGroupBlog(self, access_type, access_list, message, extra, profile_key='@NONE@'):
        """Publish a microblog with given item access
        @param access_type: one of "PUBLIC", "GROUP", "JID"
        @param access_list: list of authorized entity (empty list for PUBLIC ACCESS,
                            list of groups or list of jids) for this item
        @param message: microblog
        @param extra: dict which option name as key, which can be:
            - allow_comments: True to accept comments, False else (default: False)
            - rich: if present, contain rich text in currently selected syntax
        @profile_key: %(doc_profile_key)s
        """

        def initialised(result):
            profile, client = result
            if access_type == "PUBLIC":
                if access_list:
                    raise Exception("Publishers list must be empty when getting microblogs for all contacts")
                return self._publishMblog(client.item_access_pubsub, client, "PUBLIC", [], message, extra)
            elif access_type == "GROUP":
                _groups = set(access_list).intersection(client.roster.getGroups())  # We only keep group which actually exist
                if not _groups:
                    raise BadAccessListError("No valid group")
                return self._publishMblog(client.item_access_pubsub, client, "GROUP", _groups, message, extra)
            elif access_type == "JID":
                raise NotImplementedError
            else:
                error(_("Unknown access type"))
                raise BadAccessTypeError

        return self._initialise(profile_key).addCallback(initialised)

    def deleteGroupBlog(self, pub_data, comments, profile_key='@NONE@'):
        """Delete a microblog item from a node.
        @param pub_data: a tuple (service, node identifier, item identifier)
        @param comments: comments node identifier (for main item) or empty string
        @param profile_key: %(doc_profile_key)s
        """

        def initialised(result):
            profile, client = result
            service, node, item_id = pub_data
            service_jid = jid.JID(service) if service else client.item_access_pubsub
            if comments or not node:  # main item
                node = self.getNodeName(client.jid)
            if comments:
                # remove the associated comments node
                comments_service, comments_node = self.host.plugins["XEP-0277"].parseCommentUrl(comments)
                d = self.host.plugins["XEP-0060"].deleteNode(comments_service, comments_node, profile_key=profile)
                d.addErrback(lambda failure: error("Deletion of node %s failed: %s" % (comments_node, failure.getErrorMessage())))
            # remove the item itself
            d = self.host.plugins["XEP-0060"].retractItems(service_jid, node, [item_id], profile_key=profile)
            d.addErrback(lambda failure: error("Deletion of item %s from %s failed: %s" % (item_id, node, failure.getErrorMessage())))
            return d

        def notify(d):
            # TODO: this works only on the same host, and notifications for item deletion should be
            # implemented according to http://xmpp.org/extensions/xep-0060.html#publisher-delete-success-notify
            # instead. The notification mechanisms implemented in sat_pubsub and wokkel seem not compatible,
            # see wokkel.pubsub.PubSubClient._onEvent_items and sat_pubsub.backend._doNotifyRetraction
            service, node, item_id = pub_data
            publisher = self.host.getJidNStream(profile_key)[0]
            profile = self.host.memory.getProfileName(profile_key)
            gbdatum = {'id': item_id, 'type': 'main_item' if (comments or not node) else 'comment'}
            self.host.bridge.personalEvent(publisher.full(), "MICROBLOG_DELETE", gbdatum, profile)
            return d

        return self._initialise(profile_key).addCallback(initialised).addCallback(notify)

    def updateGroupBlog(self, pub_data, comments, message, extra, profile_key='@NONE@'):
        """Modify a microblog node
        @param pub_data: a tuple (service, node identifier, item identifier)
        @param comments: comments node identifier (for main item) or empty string
        @param message: new message
        @param extra: dict which option name as key, which can be:
            - allow_comments: True to accept an other level of comments, False else (default: False)
            - rich: if present, contain rich text in currently selected syntax
        @param profile_key: %(doc_profile)
        """

        def initialised(result):
            profile, client = result
            mblog_data = {'content': message}
            for attr in ['content_rich', 'title', 'title_rich']:
                if attr in extra and extra[attr]:
                    mblog_data[attr] = extra[attr]
            service, node, item_id = pub_data
            service_jid = jid.JID(service) if service else client.item_access_pubsub
            if comments or not node:  # main item
                node = self.getNodeName(client.jid)
            mblog_data['id'] = unicode(item_id)
            if 'published' in extra:
                mblog_data['published'] = extra['published']
            if extra.get('allow_comments', 'False').lower() == 'true':
                comments_service, comments_node = self.host.plugins["XEP-0277"].parseCommentUrl(comments)
                # we could use comments_node directly but it's safer to rebuild it
                # XXX: use the item identifier? http://bugs.goffi.org/show_bug.cgi?id=63
                entry_id = comments_node.split('_')[1].split('__')[0]
                self.__fillCommentsElement(mblog_data, entry_id, node, service_jid)
            entry_d = self.host.plugins["XEP-0277"].data2entry(mblog_data, profile)
            entry_d.addCallback(lambda mblog_item: self.host.plugins["XEP-0060"].publish(service_jid, node, items=[mblog_item], profile_key=profile))
            entry_d.addErrback(lambda failure: error("Modification of %s failed: %s" % (pub_data, failure.getErrorMessage())))
            return entry_d

        return self._initialise(profile_key).addCallback(initialised)

    def sendGroupBlogComment(self, node_url, message, extra, profile_key='@NONE@'):
        """Publish a comment in the given node
        @param node url: link to the comments node as specified in XEP-0277 and given in microblog data's comments key
        @param message: comment
        @param extra: dict which option name as key, which can be:
            - allow_comments: True to accept an other level of comments, False else (default: False)
            - rich: if present, contain rich text in currently selected syntax
        @profile_key: %(doc_profile)s
        """
        def initialised(result):
            profile, client = result
            service, node = self.host.plugins["XEP-0277"].parseCommentUrl(node_url)
            mblog_data = {'content': message}
            for attr in ['content_rich', 'title', 'title_rich']:
                if attr in extra and extra[attr]:
                    mblog_data[attr] = extra[attr]
            if 'allow_comments' in extra:
                raise NotImplementedError # TODO
            entry_d = self.host.plugins["XEP-0277"].data2entry(mblog_data, profile)
            entry_d.addCallback(lambda mblog_item: self.host.plugins["XEP-0060"].publish(service, node, items=[mblog_item], profile_key=profile))
            return entry_d

        return self._initialise(profile_key).addCallback(initialised)


    @defer.inlineCallbacks
    def _itemsConstruction(self, items, pub_jid, client):
        """ Transforms items to group blog data and manage comments node
        @param items: iterable of items
        @param pub_jid: jid of the publisher or None to use items data
        @param client: SatXMPPClient instance
        @return: deferred which fire list of group blog data """
        # TODO: use items data when pub_jid is None
        ret = []
        for item in items:
            gbdata = yield self.item2gbdata(item)
            try:
                gbdata['service'] = client.item_access_pubsub.full()
            except AttributeError:
                pass
            ret.append(gbdata)
            # if there is a comments node, we subscribe to it
            if "comments_node" in gbdata:
                try:
                    # every comments node must be subscribed, except if we are the publisher (we are already subscribed in this case)
                    if pub_jid.userhostJID() != client.jid.userhostJID():
                        self.host.plugins["XEP-0060"].subscribe(jid.JID(gbdata["comments_service"]), gbdata["comments_node"],
                                                                profile_key=client.profile)
                except KeyError:
                    warning("Missing key for comments")
        defer.returnValue(ret)

    def getLastGroupBlogs(self, pub_jid_s, max_items=10, profile_key='@NONE@'):
        """Get the last published microblogs
        @param pub_jid_s: jid of the publisher
        @param max_items: how many microblogs we want to get (see XEP-0060 #6.5.7)
        @param profile_key: profile key
        @return: list of microblog data (dict)
        """
        pub_jid = jid.JID(pub_jid_s)

        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].getItems(client.item_access_pubsub, self.getNodeName(pub_jid),
                                                       max_items=max_items, profile_key=profile_key)
            d.addCallback(self._itemsConstruction, pub_jid, client)
            d.addErrback(lambda ignore: {})  # TODO: more complete error management (log !)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self._initialise(profile_key).addCallback(initialised)

    def getLastGroupBlogsAtom(self, pub_jid_s, max_items=10, profile_key='@NONE@'):
        """Get the atom feed of the last published microblogs
        @param pub_jid: jid of the publisher
        @param max_items: how many microblogs we want to get (see XEP-0060 #6.5.7)
        @param profile_key: profile key
        @return: atom XML feed (unicode)
        """
        pub_jid = jid.JID(pub_jid_s)

        def removeAllURIs(element):
            """Recursively remove the URIs of the element and its children.
            Without that, the entry would still be valid but not displayed
            by Firefox nor Thunderbird (and probably more readers)"""
            element.uri = element.defaultUri = None
            for child in element.children:
                if isinstance(child, Element):
                    removeAllURIs(child)

        def items2feed(items, pub_jid, client):
            feed = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>%(user)s's blogposts</title>
    <link href="%(feed)s" rel="self" />
    <link href="%(blog)s" />
    <id>%(id)s</id>
    <updated>%(date)s</updated>\n""" % {'user': pub_jid.user,
                                        'feed': 'http://%s/blog/%s/atom.xml' % (client.jid.host, pub_jid.user),
                                        'blog': 'http://%s/blog/%s' % (client.jid.host, pub_jid.user),
                                        'id': self.getNodeName(pub_jid),
                                        'date': date.rfc3339.timestamp_from_tf(date.rfc3339.tf_utc())}
            for item in items:
                entry = item.firstChildElement()
                removeAllURIs(entry)
                feed += "    " + entry.toXml() + "\n"
            return feed + "</feed>"

        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].getItems(client.item_access_pubsub, self.getNodeName(pub_jid),
                                                       max_items=max_items, profile_key=profile_key)
            d.addCallback(items2feed, pub_jid, client)
            d.addErrback(lambda ignore: {})  # TODO: more complete error management (log !)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self._initialise(profile_key).addCallback(initialised)

    def getGroupBlogComments(self, service_s, node, profile_key='@NONE@'):
        """Get all comments of given node
        @param service_s: service hosting the node
        @param node: comments node
        @param profile_key: profile key
        @return: list of microblog data (dict)
        """
        service = jid.JID(service_s)

        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].getItems(service, node,
                                                       profile_key=profile_key)
            d.addCallback(self._handleCommentsItems, service, node)
            d.addErrback(lambda ignore: {})  # TODO: more complete error management (log !)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self._initialise(profile_key).addCallback(initialised)

    def _getMassiveLastGroupBlogs(self, publishers_type, publishers, max_items=10, profile_key='@NONE@'):
        if publishers_type == 'JID':
            publishers_jids = [jid.JID(publisher) for publisher in publishers]
        else:
            publishers_jids = publishers
        return self.getMassiveLastGroupBlogs(publishers_type, publishers_jids, max_items, profile_key)

    def getMassiveLastGroupBlogs(self, publishers_type, publishers, max_items=10, profile_key='@NONE@'):
        """Get the last published microblogs for a list of groups or jids
        @param publishers_type: type of the list of publishers (one of "GROUP" or "JID" or "ALL")
        @param publishers: list of publishers, according to "publishers_type" (list of groups or list of jids)
        @param max_items: how many microblogs we want to get
        @param profile_key: profile key
        """

        def sendResult(result):
            """send result of DeferredList (list of microblogs to the calling method"""

            ret = {}

            for (success, value) in result:
                if success:
                    source_jid, data = value
                    ret[source_jid] = data

            return ret

        def initialised(result):
            profile, client = result

            if publishers_type == "ALL":
                contacts = client.roster.getItems()
                jids = [contact.jid.userhostJID() for contact in contacts]
            elif publishers_type == "GROUP":
                jids = []
                for _group in publishers:
                    jids.extend(client.roster.getJidsFromGroup(_group))
            elif publishers_type == 'JID':
                jids = publishers
            else:
                raise UnknownType

            mblogs = []


            for jid_ in jids:
                d = self.host.plugins["XEP-0060"].getItems(client.item_access_pubsub, self.getNodeName(jid_),
                                                           max_items=max_items, profile_key=profile_key)
                d.addCallback(self._itemsConstruction, jid_, client)
                d.addCallback(lambda gbdata, source_jid: (source_jid, gbdata), jid_.full())

                mblogs.append(d)
            # consume the failure "StanzaError with condition u'item-not-found'"
            # when the node doesn't exist (e.g that JID hasn't posted any message)
            dlist = defer.DeferredList(mblogs, consumeErrors=True)
            dlist.addCallback(sendResult)

            return dlist

        #TODO: custom exception
        if publishers_type not in ["GROUP", "JID", "ALL"]:
            raise Exception("Bad call, unknown publishers_type")
        if publishers_type == "ALL" and publishers:
            raise Exception("Publishers list must be empty when getting microblogs for all contacts")
        return self._initialise(profile_key).addCallback(initialised)
        #TODO: we need to use the server corresponding the the host of the jid

    def subscribeGroupBlog(self, pub_jid, profile_key='@NONE@'):
        def initialised(result):
            profile, client = result
            d = self.host.plugins["XEP-0060"].subscribe(client.item_access_pubsub, self.getNodeName(jid.JID(pub_jid)),
                                                        profile_key=profile_key)
            return d

        #TODO: we need to use the server corresponding the the host of the jid
        return self._initialise(profile_key).addCallback(initialised)

    def _massiveSubscribeGroupBlogs(self, publishers_type, publishers, profile_key='@NONE@'):
        if publishers_type == 'JID':
            publishers_jids = [jid.JID(publisher) for publisher in publishers]
        else:
            publishers_jids = publishers
        return self.massiveSubscribeGroupBlogs(publishers_type, publishers_jids, profile_key)

    def massiveSubscribeGroupBlogs(self, publishers_type, publishers, profile_key='@NONE@'):
        """Subscribe microblogs for a list of groups or jids
        @param publishers_type: type of the list of publishers (one of "GROUP" or "JID" or "ALL")
        @param publishers: list of publishers, according to "publishers_type" (list of groups or list of jids)
        @param profile_key: profile key
        """

        def initialised(result):
            profile, client = result

            if publishers_type == "ALL":
                contacts = client.roster.getItems()
                jids = [contact.jid.userhostJID() for contact in contacts]
            elif publishers_type == "GROUP":
                jids = []
                for _group in publishers:
                    jids.extend(client.roster.getJidsFromGroup(_group))
            elif publishers_type == 'JID':
                jids = publishers
            else:
                raise UnknownType

            mblogs = []
            for jid_ in jids:
                d = self.host.plugins["XEP-0060"].subscribe(client.item_access_pubsub, self.getNodeName(jid_),
                                                            profile_key=profile_key)
                mblogs.append(d)
            # consume the failure "StanzaError with condition u'item-not-found'"
            # when the node doesn't exist (e.g that JID hasn't posted any message)
            dlist = defer.DeferredList(mblogs, consumeErrors=True)
            return dlist

        #TODO: custom exception
        if publishers_type not in ["GROUP", "JID", "ALL"]:
            raise Exception("Bad call, unknown publishers_type")
        if publishers_type == "ALL" and publishers:
            raise Exception("Publishers list must be empty when getting microblogs for all contacts")
        return self._initialise(profile_key).addCallback(initialised)
        #TODO: we need to use the server corresponding the the host of the jid


class GroupBlog_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_GROUPBLOG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []
