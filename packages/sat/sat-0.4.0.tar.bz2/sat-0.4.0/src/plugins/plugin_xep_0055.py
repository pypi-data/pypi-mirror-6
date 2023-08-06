#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for Jabber Search (xep-0055)
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
from twisted.words.protocols.jabber.xmlstream import IQ
from twisted.words.protocols.jabber import jid
from wokkel import data_form
from sat.core.exceptions import DataError
from sat.memory.memory import Sessions
from sat.tools import xml_tools

NS_SEARCH = 'jabber:iq:search'

PLUGIN_INFO = {
    "name": "Jabber Search",
    "import_name": "XEP-0055",
    "type": "XEP",
    "protocols": ["XEP-0055"],
    "main": "XEP_0055",
    "handler": "no",
    "description": _("""Implementation of Jabber Search""")
}


class XEP_0055(object):

    def __init__(self, host):
        info(_("Jabber search plugin initialization"))
        self.host = host
        host.bridge.addMethod("getSearchUI", ".plugin", in_sign='ss', out_sign='s',
                              method=self._getSearchUI,
                              async=True)
        host.bridge.addMethod("searchRequest", ".plugin", in_sign='sa{ss}s', out_sign='s',
                              method=self._searchRequest,
                              async=True)
        self._sessions = Sessions()
        self.__menu_cb_id = host.registerCallback(self._menuCb, with_data=True)
        self.__search_request_id = host.registerCallback(self._xmluiSearchRequest, with_data=True)
        host.importMenu((D_("Communication"), D_("Search directory")), self._searchMenu, security_limit=1, help_string=D_("Search use directory"))

    def _menuCb(self, data, profile):
        entity = jid.JID(data[xml_tools.SAT_FORM_PREFIX+'jid'])
        d = self.getSearchUI(entity, profile)
        def gotXMLUI(xmlui):
            session_id, session_data = self._sessions.newSession(profile=profile)
            session_data['jid'] = entity
            xmlui.session_id = session_id # we need to keep track of the session
            xmlui.submit_id = self.__search_request_id
            return {'xmlui': xmlui.toXml()}
        d.addCallback(gotXMLUI)
        return d


    def _searchMenu(self, menu_data, profile):
        """ First XMLUI activated by menu: ask for target jid
        @param profile: %(doc_profile)s

        """
        form_ui = xml_tools.XMLUI("form", title=_("Search directory"), submit_id=self.__menu_cb_id)
        form_ui.addText(_("Please enter the search jid"), 'instructions')
        form_ui.changeContainer("pairs")
        form_ui.addLabel("jid")
        # form_ui.addString("jid", value="users.jabberfr.org") # TODO: replace users.jabberfr.org by any XEP-0055 compatible service discovered on current server
        form_ui.addString("jid", value="salut.libervia.org") # TODO: replace salut.libervia.org by any XEP-0055 compatible service discovered on current server
        return {'xmlui': form_ui.toXml()}

    def _getSearchUI(self, to_jid_s, profile_key):
        d = self.getSearchUI(jid.JID(to_jid_s), profile_key)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def getSearchUI(self, to_jid, profile_key):
        """ Ask for a search interface
        @param to_jid: XEP-0055 compliant search entity
        @param profile_key: %(doc_profile_key)s
        @return: XMLUI search interface """
        client = self.host.getClient(profile_key)
        fields_request = IQ(client.xmlstream, 'get')
        fields_request["from"] = client.jid.full()
        fields_request["to"] = to_jid.full()
        fields_request.addElement('query', NS_SEARCH)
        d = fields_request.send(to_jid.full())
        d.addCallbacks(self._fieldsOk, self._fieldsErr, callbackArgs=[client.profile], errbackArgs=[client.profile])
        return d

    def _fieldsOk(self, answer, profile):
        """got fields available"""
        try:
            query_elts = answer.elements('jabber:iq:search', 'query').next()
        except StopIteration:
            info(_("No query element found"))
            raise DataError # FIXME: StanzaError is probably more appropriate, check the RFC
        try:
            form_elt = query_elts.elements(data_form.NS_X_DATA, 'x').next()
        except StopIteration:
            info(_("No data form found"))
            raise NotImplementedError("Only search through data form is implemented so far")
        parsed_form = data_form.Form.fromElement(form_elt)
        return xml_tools.dataForm2XMLUI(parsed_form, "")

    def _fieldsErr(self, failure, profile):
        """ Called when something is wrong with fields request """
        info(_("Fields request failure: %s") % str(failure.value))
        return failure

    def _xmluiSearchRequest(self, raw_data, profile):
        try:
            session_data = self._sessions.profileGet(raw_data["session_id"], profile)
        except KeyError:
            warning ("session id doesn't exist, session has probably expired")
            # TODO: send error dialog
            return defer.succeed({})

        data = xml_tools.XMLUIResult2DataFormResult(raw_data)
        entity =session_data['jid']
        d = self.searchRequest(entity, data, profile)
        d.addCallback(lambda xmlui: {'xmlui':xmlui.toXml()})
        del self._sessions[raw_data["session_id"]]
        return d

    def _searchRequest(self, to_jid_s, search_dict, profile_key):
        d = self.searchRequest(jid.JID(to_jid_s), search_dict, profile_key)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def searchRequest(self, to_jid, search_dict, profile_key):
        """ Actually do a search, according to filled data
        @param to_jid: XEP-0055 compliant search entity
        @param search_dict: filled data, corresponding to the form obtained in getSearchUI
        @param profile_key: %(doc_profile_key)s
        @return: XMLUI search result """
        client = self.host.getClient(profile_key)
        search_request = IQ(client.xmlstream, 'set')
        search_request["from"] = client.jid.full()
        search_request["to"] = to_jid.full()
        query_elt = search_request.addElement('query', NS_SEARCH)
        x_form = data_form.Form('submit', formNamespace = NS_SEARCH)
        x_form.makeFields(search_dict)
        query_elt.addChild(x_form.toElement())
        d = search_request.send(to_jid.full())
        d.addCallbacks(self._searchOk, self._searchErr, callbackArgs=[client.profile], errbackArgs=[client.profile])
        return d

    def _searchOk(self, answer, profile):
        """got search available"""
        try:
            query_elts = answer.elements('jabber:iq:search', 'query').next()
        except StopIteration:
            info(_("No query element found"))
            raise DataError # FIXME: StanzaError is probably more appropriate, check the RFC
        try:
            form_elt = query_elts.elements(data_form.NS_X_DATA, 'x').next()
        except StopIteration:
            info(_("No data form found"))
            raise NotImplementedError("Only search through data form is implemented so far")
        return xml_tools.dataFormResult2XMLUI(form_elt)

    def _searchErr(self, failure, profile):
        """ Called when something is wrong with search request """
        info(_("Search request failure: %s") % str(failure.value))
        return failure
