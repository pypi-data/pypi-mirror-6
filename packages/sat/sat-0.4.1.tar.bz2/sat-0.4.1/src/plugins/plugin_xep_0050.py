#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for Ad-Hoc Commands (XEP-0050)
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

from sat.core.i18n import _, D_
from logging import debug, info, warning, error
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as xmpp_error
from twisted.words.xish import domish
from twisted.internet import defer, reactor
from wokkel import disco, iwokkel, data_form, compat
from sat.core import exceptions
from sat.memory.memory import Sessions
from uuid import uuid4
from sat.tools import xml_tools

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from collections import namedtuple

try:
    from collections import OrderedDict # only available from python 2.7
except ImportError:
    from ordereddict import OrderedDict

IQ_SET = '/iq[@type="set"]'
NS_COMMANDS = "http://jabber.org/protocol/commands"
ID_CMD_LIST = disco.DiscoIdentity("automation", "command-list")
ID_CMD_NODE = disco.DiscoIdentity("automation", "command-node")
CMD_REQUEST = IQ_SET + '/command[@xmlns="' + NS_COMMANDS + '"]'

SHOWS = OrderedDict([('default', _('Online')),
                     ('away', _('Away')),
                     ('chat', _('Free for chat')),
                     ('dnd', _('Do not disturb')),
                     ('xa', _('Left')),
                     ('disconnect', _('Disconnect'))])

PLUGIN_INFO = {
    "name": "Ad-Hoc Commands",
    "import_name": "XEP-0050",
    "type": "XEP",
    "protocols": ["XEP-0050"],
    "main": "XEP_0050",
    "handler": "yes",
    "description": _("""Implementation of Ad-Hoc Commands""")
}


class AdHocError(Exception):

    def __init__(self, error_const):
        """ Error to be used from callback
        @param error_const: one of XEP_0050.ERROR
        """
        assert(error_const in XEP_0050.ERROR)
        self.callback_error = error_const

class AdHocCommand(XMPPHandler):
    implements(iwokkel.IDisco)

    def  __init__(self, parent, callback, label, node, features, timeout, allowed_jids, allowed_groups, allowed_magics, forbidden_jids, forbidden_groups, client):
        self.parent = parent
        self.callback = callback
        self.label = label
        self.node = node
        self.features = [disco.DiscoFeature(feature) for feature in features]
        self.allowed_jids, self.allowed_groups, self.allowed_magics, self.forbidden_jids, self.forbidden_groups = allowed_jids, allowed_groups, allowed_magics, forbidden_jids, forbidden_groups
        self.client = client
        self.sessions = Sessions(timeout=timeout)

    def getName(self, xml_lang=None):
        return self.label

    def isAuthorised(self, requestor):
        if '@ALL@' in self.allowed_magics:
            return True
        forbidden = set(self.forbidden_jids)
        for group in self.forbidden_groups:
            forbidden.update(self.client.roster.getJidsFromGroup(group))
        if requestor.userhostJID() in forbidden:
            return False
        allowed = set(self.allowed_jids)
        for group in self.allowed_groups:
            try:
                allowed.update(self.client.roster.getJidsFromGroup(group))
            except exceptions.UnknownGroupError:
                warning(_("The groups [%(group)s] is unknown for profile [%(profile)s])" % {'group':group, 'profile':self.client.profile}))
        if requestor.userhostJID() in allowed:
            return True
        return False

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        identities = [ID_CMD_LIST if self.node == NS_COMMANDS else ID_CMD_NODE]
        return [disco.DiscoFeature(NS_COMMANDS)] + self.features

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        return []

    def _sendAnswer(self, callback_data, session_id, request):
        """ Send result of the command
        @param callback_data: tuple (payload, status, actions, note) with:
            - payload (domish.Element) usualy containing data form
            - status: current status, see XEP_0050.STATUS
            - actions: list of allowed actions (see XEP_0050.ACTION). First action is the default one. Default to EXECUTE
            - note: optional additional note: either None or a tuple with (note type, human readable string),
                    note type being in XEP_0050.NOTE
        @param session_id: current session id
        @param request: original request (domish.Element)
        @return: deferred
        """
        payload, status, actions, note = callback_data
        assert(isinstance(payload, domish.Element) or payload is None)
        assert(status in XEP_0050.STATUS)
        if not actions:
            actions = [XEP_0050.ACTION.EXECUTE]
        result = domish.Element((None, 'iq'))
        result['type'] = 'result'
        result['id'] = request['id']
        result['to'] = request['from']
        command_elt = result.addElement('command', NS_COMMANDS)
        command_elt['sessionid'] = session_id
        command_elt['node'] = self.node
        command_elt['status'] = status

        if status != XEP_0050.STATUS.CANCELED:
            if status != XEP_0050.STATUS.COMPLETED:
                actions_elt = command_elt.addElement('actions')
                actions_elt['execute'] = actions[0]
                for action in actions:
                    actions_elt.addElement(action)

            if note is not None:
                note_type, note_mess = note
                note_elt = command_elt.addElement('note', content=note_mess)
                note_elt['type'] = note_type

            if payload is not None:
                command_elt.addChild(payload)

        self.client.xmlstream.send(result)
        if status in (XEP_0050.STATUS.COMPLETED, XEP_0050.STATUS.CANCELED):
            del self.sessions[session_id]

    def _sendError(self, error_constant, session_id, request):
        """ Send error stanza
        @param error_constant: one of XEP_OO50.ERROR
        @param request: original request (domish.Element)
        """
        xmpp_condition, cmd_condition = error_constant
        iq_elt = xmpp_error.StanzaError(xmpp_condition).toResponse(request)
        if cmd_condition:
            error_elt = iq_elt.elements(None, "error").next()
            error_elt.addElement(cmd_condition, NS_COMMANDS)
        self.client.xmlstream.send(iq_elt)
        del self.sessions[session_id]

    def onRequest(self, command_elt, requestor, action, session_id):
        if not self.isAuthorised(requestor):
            return self._sendError(XEP_0050.ERROR.FORBIDDEN, session_id, command_elt.parent)
        if session_id:
            try:
                session_data = self.sessions[session_id]
            except KeyError:
                return self._sendError(XEP_0050.ERROR.SESSION_EXPIRED, session_id, command_elt.parent)
            if session_data['requestor'] != requestor:
                return self._sendError(XEP_0050.ERROR.FORBIDDEN, session_id, command_elt.parent)
        else:
            session_id, session_data = self.sessions.newSession()
            session_data['requestor'] = requestor
        if action == XEP_0050.ACTION.CANCEL:
            d = defer.succeed((None, XEP_0050.STATUS.CANCELED, None, None))
        else:
            d = defer.maybeDeferred(self.callback, command_elt, session_data, action, self.node, self.client.profile)
        d.addCallback(self._sendAnswer, session_id, command_elt.parent)
        d.addErrback(lambda failure, request: self._sendError(failure.value.callback_error, session_id, request), command_elt.parent)


class XEP_0050(object):
    STATUS = namedtuple('Status', ('EXECUTING', 'COMPLETED', 'CANCELED'))('executing', 'completed', 'canceled')
    ACTION = namedtuple('Action', ('EXECUTE', 'CANCEL', 'NEXT', 'PREV'))('execute', 'cancel', 'next', 'prev')
    NOTE = namedtuple('Note', ('INFO','WARN','ERROR'))('info','warn','error')
    ERROR = namedtuple('Error', ('MALFORMED_ACTION', 'BAD_ACTION', 'BAD_LOCALE', 'BAD_PAYLOAD', 'BAD_SESSIONID', 'SESSION_EXPIRED',
                                 'FORBIDDEN', 'ITEM_NOT_FOUND', 'FEATURE_NOT_IMPLEMENTED', 'INTERNAL'))(('bad-request', 'malformed-action'),
                                 ('bad-request', 'bad-action'), ('bad-request', 'bad-locale'), ('bad-request','bad-payload'),
                                 ('bad-request','bad-sessionid'), ('not-allowed','session-expired'), ('forbidden', None),
                                 ('item-not-found', None), ('feature-not-implemented', None), ('internal-server-error', None)) # XEP-0050 §4.6 Table 5

    def __init__(self, host):
        info(_("plugin XEP-0050 initialization"))
        self.host = host
        self.requesting = Sessions()
        self.answering = {}
        host.bridge.addMethod("requestCommand", ".plugin", in_sign='ss', out_sign='s',
                              method=self._requestCommandsList,
                              async=True)
        self.__requesting_id = host.registerCallback(self._requestingEntity, with_data=True)
        host.importMenu((D_("Service"), D_("commands")), self._commandsMenu, security_limit=4, help_string=D_("Execute ad-hoc commands"))

    def getHandler(self, profile):
        return XEP_0050_handler(self)

    def profileConnected(self, profile):
        self.addAdHocCommand(self._statusCallback, _("Status"), profile_key=profile)

    def profileDisconnected(self, profile):
        try:
            del self.answering[profile]
        except KeyError:
            pass

    def _items2XMLUI(self, items):
        """ Convert discovery items to XMLUI dialog """
        # TODO: manage items on different jids
        form_ui = xml_tools.XMLUI("form", submit_id=self.__requesting_id)

        form_ui.addText(_("Please select a command"), 'instructions')

        options = [(item.nodeIdentifier, item.name) for item in items]
        form_ui.addList("node", options)
        return form_ui

    def _commandsAnswer2XMLUI(self, iq_elt, session_id, session_data):
        """
        Convert command answer to an ui for frontend
        @param iq_elt: command result
        @param session_id: id of the session used with the frontend
        @param profile_key: %(doc_profile_key)s

        """
        command_elt = iq_elt.elements(NS_COMMANDS, "command").next()
        status = command_elt.getAttribute('status', XEP_0050.STATUS.EXECUTING)
        if status in [XEP_0050.STATUS.COMPLETED, XEP_0050.STATUS.CANCELED]:
            # the command session is finished, we purge our session
            del self.requesting[session_id]
            return None
        remote_session_id = command_elt.getAttribute('sessionid')
        if remote_session_id:
            session_data['remote_id'] = remote_session_id
        data_elt = command_elt.elements(data_form.NS_X_DATA, 'x').next()
        form = data_form.Form.fromElement(data_elt)
        return  xml_tools.dataForm2XMLUI(form, self.__requesting_id, session_id=session_id)

    def _requestingEntity(self, data, profile):
        """
        request and entity and create XMLUI accordingly
        @param data: data returned by previous XMLUI (first one must come from self._commandsMenu)
        @param profile: %(doc_profile)s
        @return: callback dict result (with "xmlui" corresponding to the answering dialog, or empty if it's finished without error)

        """
        # TODO: cancel, prev and next are not managed
        # TODO: managed answerer errors
        # TODO: manage nodes with a non data form payload
        if "session_id" not in data:
            # we just had the jid, we now request it for the available commands
            session_id, session_data = self.requesting.newSession(profile=profile)
            entity = jid.JID(data[xml_tools.SAT_FORM_PREFIX+'jid'])
            session_data['jid'] = entity
            d = self.requestCommandsList(entity, profile)

            def sendItems(xmlui):
                xmlui.session_id = session_id # we need to keep track of the session
                return {'xmlui': xmlui.toXml()}

            d.addCallback(sendItems)
        else:
            # we have started a several forms sessions
            try:
                session_data = self.requesting.profileGet(data["session_id"], profile)
            except KeyError:
                warning ("session id doesn't exist, session has probably expired")
                # TODO: send error dialog
                return defer.succeed({})
            session_id = data["session_id"]
            entity = session_data['jid']
            try:
                node = session_data['node']
                # node has already been received
            except KeyError:
                # it's the first time we know the node, we save it in session data
                node = session_data['node'] = data[xml_tools.SAT_FORM_PREFIX+'node']

            client = self.host.getClient(profile)
            if not client:
                raise exceptions.ProfileUnknownError

            # we request execute node's command
            iq_elt = compat.IQ(client.xmlstream, 'set')
            iq_elt['to'] = entity.full()
            command_elt = iq_elt.addElement("command", NS_COMMANDS)
            command_elt['node'] = session_data['node']
            command_elt['action'] = XEP_0050.ACTION.EXECUTE
            try:
                # remote_id is the XEP_0050 sessionid used by answering command
                # while session_id is our own session id used with the frontend
                command_elt['sessionid'] = session_data['remote_id']
            except KeyError:
                pass

            command_elt.addChild(xml_tools.XMLUIResultToElt(data)) # We add the XMLUI result to the command payload
            d = iq_elt.send()
            d.addCallback(self._commandsAnswer2XMLUI, session_id, session_data)
            d.addCallback(lambda xmlui: {'xmlui': xmlui.toXml()} if xmlui is not None else {})

        return d

    def _commandsMenu(self, menu_data, profile):
        """ First XMLUI activated by menu: ask for target jid
        @param profile: %(doc_profile)s

        """
        form_ui = xml_tools.XMLUI("form", submit_id=self.__requesting_id)
        form_ui.addText(_("Please enter target jid"), 'instructions')
        form_ui.changeContainer("pairs")
        form_ui.addLabel("jid")
        form_ui.addString("jid")
        return {'xmlui': form_ui.toXml()}

    def _statusCallback(self, command_elt, session_data, action, node, profile):
        """ Ad-hoc command used to change the "show" part of status """
        actions = session_data.setdefault('actions',[])
        actions.append(action)

        if len(actions) == 1:
            # it's our first request, we ask the desired new status
            status = XEP_0050.STATUS.EXECUTING
            form = data_form.Form('form', title=_('status selection'))
            show_options = [data_form.Option(name, label) for name, label in SHOWS.items()]
            field = data_form.Field('list-single', 'show', options=show_options, required=True)
            form.addField(field)

            payload = form.toElement()
            note = None

        elif len(actions) == 2:
            # we should have the answer here
            try:
                x_elt = command_elt.elements(data_form.NS_X_DATA,'x').next()
                answer_form = data_form.Form.fromElement(x_elt)
                show = answer_form['show']
            except KeyError, StopIteration:
                raise AdHocError(XEP_0050.ERROR.BAD_PAYLOAD)
            if show not in SHOWS:
                raise AdHocError(XEP_0050.ERROR.BAD_PAYLOAD)
            if show == "disconnect":
               self.host.disconnect(profile)
            else:
                self.host.setPresence(show=show, profile_key=profile)

            # job done, we can end the session
            form = data_form.Form('form', title=_(u'Updated'))
            form.addField(data_form.Field('fixed', u'Status updated'))
            status = XEP_0050.STATUS.COMPLETED
            payload = None
            note = (self.NOTE.INFO, _(u"Status updated"))
        else:
            raise AdHocError(XEP_0050.ERROR.INTERNAL)

        return (payload, status, None, note)

    def _requestCommandsList(self, to_jid_s, profile_key):
        d = self.requestCommandsList(jid.JID(to_jid_s), profile_key)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def requestCommandsList(self, to_jid, profile_key):
        """ Request available commands
        @param to_jid: the entity answering the commands
        @param profile_key: %(doc_profile)s

        """
        client = self.host.getClient(profile_key)
        d = client.disco.requestItems(to_jid, NS_COMMANDS)
        d.addCallback(self._items2XMLUI)
        return d

    def addAdHocCommand(self, callback, label, node="", features = None, timeout = 600, allowed_jids = None, allowed_groups = None,
                        allowed_magics = None, forbidden_jids = None, forbidden_groups = None, profile_key="@NONE@"):
        """

        Add an ad-hoc command for the current profile

        @param callback: method associated with this ad-hoc command which return the payload data (see AdHocCommand._sendAnswer), can return a deferred
        @param label: label associated with this command on the main menu
        @param node: disco item node associated with this command. None or "" to use autogenerated node
        @param features: features associated with the payload (list of strings), usualy data form
        @param timeout: delay between two requests before canceling the session (in seconds)
        @param allowed_jids: list of allowed entities
        @param allowed_groups: list of allowed roster groups
        @param allowed_magics: list of allowed magic keys, can be:
                               @ALL@: allow everybody
                               @PROFILE_BAREJID@: allow only the jid of the profile
        @param forbidden_jids: black list of entities which can't access this command
        @param forbidden_groups: black list of groups which can't access this command
        @param profile_key: profile key associated with this command, @ALL@ means can be accessed with every profiles
        @return: node of the added command, useful to remove the command later
        """
        # FIXME: "@ALL@" for profile_key seems useless and dangerous

        node = node.strip()
        if not node:
            node = "%s_%s" % ('COMMANDS', uuid4())

        if features is None:
            features = [data_form.NS_X_DATA]

        if allowed_jids is None:
            allowed_jids = []
        if allowed_groups is None:
            allowed_groups = []
        if allowed_magics is None:
            allowed_magics = ['@PROFILE_BAREJID@']
        if forbidden_jids is None:
            forbidden_jids = []
        if forbidden_groups is None:
            forbidden_groups = []

        for client in self.host.getClients(profile_key):
            #TODO: manage newly created/removed profiles
            _allowed_jids = (allowed_jids + [client.jid.userhostJID()]) if '@PROFILE_BAREJID@' in allowed_magics else allowed_jids
            ad_hoc_command = AdHocCommand(self, callback, label, node, features, timeout, _allowed_jids,
                                          allowed_groups, allowed_magics, forbidden_jids, forbidden_groups, client)
            ad_hoc_command.setHandlerParent(client)
            profile_commands = self.answering.setdefault(client.profile, {})
            profile_commands[node] = ad_hoc_command

    def onCmdRequest(self, request, profile):
        request.handled = True
        requestor = jid.JID(request['from'])
        command_elt = request.elements(NS_COMMANDS, 'command').next()
        action = command_elt.getAttribute('action', self.ACTION.EXECUTE)
        node = command_elt.getAttribute('node')
        if not node:
            raise exceptions.DataError
        sessionid = command_elt.getAttribute('sessionid')
        try:
            command = self.answering[profile][node]
        except KeyError:
            raise exceptions.DataError
        command.onRequest(command_elt, requestor, action, sessionid)


class XEP_0050_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(CMD_REQUEST, self.plugin_parent.onCmdRequest, profile=self.parent.profile)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        identities = []
        if nodeIdentifier == NS_COMMANDS and self.plugin_parent.answering.get(self.parent.profile): # we only add the identity if we have registred commands
            identities.append(ID_CMD_LIST)
        return [disco.DiscoFeature(NS_COMMANDS)] + identities

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        ret = []
        if nodeIdentifier == NS_COMMANDS:
            for command in self.plugin_parent.answering.get(self.parent.profile,{}).values():
                if command.isAuthorised(requestor):
                    ret.append(disco.DiscoItem(self.parent.jid, command.node, command.getName())) #TODO: manage name language
        return ret
