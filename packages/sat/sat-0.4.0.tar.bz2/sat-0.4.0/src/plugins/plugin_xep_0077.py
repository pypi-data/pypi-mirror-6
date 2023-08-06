#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0077
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
from logging import debug, info, warning, error
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import IQ
from sat.tools import xml_tools
from sat.memory import memory

from wokkel import data_form, compat

NS_REG = 'jabber:iq:register'

PLUGIN_INFO = {
    "name": "XEP 0077 Plugin",
    "import_name": "XEP-0077",
    "type": "XEP",
    "protocols": ["XEP-0077"],
    "dependencies": [],
    "main": "XEP_0077",
    "description": _("""Implementation of in-band registration""")
}


class XEP_0077(object):

    def __init__(self, host):
        info(_("Plugin XEP_0077 initialization"))
        self.host = host
        self.triggers = {}  # used by other protocol (e.g. XEP-0100) to finish registration. key = target_jid
        host.bridge.addMethod("inBandRegister", ".plugin", in_sign='ss', out_sign='s',
                              method=self._inBandRegister,
                              async=True)

    def _regOk(self, answer, client, post_treat_cb):
        """Called after the first get IQ"""
        try:
            query_elt = answer.elements(NS_REG, 'query').next()
        except StopIteration:
            raise exceptions.DataError("Can't find expected query element")

        try:
            x_elem = query_elt.elements(data_form.NS_X_DATA, 'x').next()
        except StopIteration:
            # XXX: it seems we have an old service which doesn't manage data forms
            warning(_("Can't find data form"))
            raise exceptions.DataError(_("This gateway can't be managed by SàT, sorry :("))

        def submitForm(data, profile):
            form_elt = xml_tools.XMLUIResultToElt(data)

            iq_elt = compat.IQ(client.xmlstream, 'set')
            iq_elt['id'] = answer['id']
            iq_elt['to'] = answer['from']
            query_elt = iq_elt.addElement("query", NS_REG)
            query_elt.addChild(form_elt)
            d = iq_elt.send()
            d.addCallback(self._regSuccess, client, post_treat_cb)
            d.addErrback(self._regFailure, client)
            return d

        form = data_form.Form.fromElement(x_elem)
        submit_reg_id = self.host.registerCallback(submitForm, with_data=True, one_shot=True)
        return xml_tools.dataForm2XMLUI(form, submit_reg_id)

    def _regErr(self, failure, client):
        """Called when something is wrong with registration"""
        info(_("Registration failure: %s") % str(failure.value))
        raise failure

    def _regSuccess(self, answer, client, post_treat_cb):
        debug(_("registration answer: %s") % answer.toXml())
        if post_treat_cb is not None:
            post_treat_cb(jid.JID(answer['from']), client.profile)
        return {}

    def _regFailure(self, failure, client):
        info(_("Registration failure: %s") % str(failure.value))
        if failure.value.condition == 'conflict':
            raise exceptions.ConflictError( _("Username already exists, please choose an other one"))
        raise failure

    def _inBandRegister(self, to_jid_s, profile_key='@NONE@'):
        return self.inBandRegister, jid.JID(to_jid_s, profile_key)

    def inBandRegister(self, to_jid, post_treat_cb=None, profile_key='@NONE@'):
        """register to a target JID"""
        client = self.host.getClient(profile_key)
        if not client:
            raise exceptions.ProfileUnknownError
        debug(_("Asking registration for [%s]") % to_jid.full())
        reg_request = IQ(client.xmlstream, 'get')
        reg_request["from"] = client.jid.full()
        reg_request["to"] = to_jid.full()
        reg_request.addElement('query', NS_REG)
        d = reg_request.send(to_jid.full()).addCallbacks(self._regOk, self._regErr, callbackArgs=[client, post_treat_cb], errbackArgs=[client])
        return d
