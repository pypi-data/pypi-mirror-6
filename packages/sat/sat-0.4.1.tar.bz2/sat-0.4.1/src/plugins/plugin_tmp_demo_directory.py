#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for account creation (experimental)
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
from twisted.internet import defer
from twisted.words.protocols.jabber.xmlstream import IQ
from twisted.words.protocols.jabber import jid
from wokkel import data_form

PLUGIN_INFO = {
    "name": "Demo directory plugin",
    "import_name": "DEMO-DIRECTORY",
    "type": "TMP",
    "protocols": [],
    "dependencies": [],
    "main": "DemoDirectory",
    "handler": "no",
    "description": _(u"""Plugin to add paramaters to subscribe to the demo directory""")
}

NS_COMMANDS = "http://jabber.org/protocol/commands"

CONFIG_SECTION = "plugin demo directory"
CONFIG_ACTIVATE = "activate"
CONFIG_SERVICE = "service"

PARAM_CATEGORY = ("directory", D_("Directory"))
PARAM_NAME_INFO = D_("To appear on the directory, check the box. To be removed from the directory, just uncheck it.")
PARAM_NAME_DESC = ("description", D_("Some words about you"))
PARAM_NAME_SUB = ("subscribe", D_("I want to appear in the public demo directory"))



class DemoDirectory(object):
    """Account plugin: create a SàT + Prosody account, used by Libervia"""
    # XXX: This plugin is a Q&D one used for the demo.
    # TODO: A generic way to add menu/parameters for local services would be nice

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param label="%(info)s" type="text" security="1" />
        <param name="%(desc)s" label="%(desc_label)s" type="string" security="1" />
        <param name="%(sub)s" label="%(sub_label)s" value='false' type="bool" security="1" />
     </category>
    </individual>
    </params>
    """ % {
        'category_name': PARAM_CATEGORY[0],
        'category_label': _(PARAM_CATEGORY[1]),
        'info': _(PARAM_NAME_INFO),
        'desc': PARAM_NAME_DESC[0],
        'desc_label': _(PARAM_NAME_DESC[1]),
        'sub': PARAM_NAME_SUB[0],
        'sub_label': _(PARAM_NAME_SUB[1]),
    }

    def __init__(self, host):
        info(_(u"Plugin demo directory initialization"))
        activate = host.memory.getConfig(CONFIG_SECTION, CONFIG_ACTIVATE) or 'false'
        if not activate.lower() in ('true', 'yes', '1'):
            info("not activated")
            return
        service_str = host.memory.getConfig(CONFIG_SECTION, CONFIG_SERVICE) or 'salut.libervia.org'
        self.service = jid.JID(service_str)
        self.host = host
        host.memory.updateParams(self.params)
        host.trigger.add("paramUpdateTrigger", self.paramUpdateTrigger)

    @defer.inlineCallbacks
    def manageSubscription(self, subscribe, profile):
        """ Subscribe or unsubscribe according to subscribe value
        This follow the implementation of the "Salut", this is not for general purpose
        @param subscribe: True to subscribe, else unsubscribe
        @param profile: %(doc_profile)s

        """
        client = self.host.getClient(profile)
        if not subscribe:
            info ("Unsubscribing [%s] from directory" % profile)
            unsub_req = IQ(client.xmlstream, 'set')
            unsub_req['from'] = client.jid.full()
            unsub_req['to'] = self.service.userhost()
            command_elt = unsub_req.addElement('command', NS_COMMANDS)
            command_elt['node'] = 'unsubscribe'
            command_elt['action'] = 'execute'
            yield unsub_req.send(self.service.userhost())
        else:
            info ("Subscribing [%s] to directory" % profile)
            sub_req = IQ(client.xmlstream, 'set')
            sub_req['from'] = client.jid.full()
            sub_req['to'] = self.service.userhost()
            command_elt = sub_req.addElement('command', NS_COMMANDS)
            command_elt['node'] = 'subscribe'
            command_elt['action'] = 'execute'
            sub_first_elt = yield sub_req.send(self.service.userhost())
            sub_cmd = sub_first_elt.elements(NS_COMMANDS, 'command').next()
            session_id = sub_cmd['sessionid']
            sub_req = IQ(client.xmlstream, 'set')
            sub_req['from'] = client.jid.full()
            sub_req['to'] = self.service.userhost()
            command_elt = sub_req.addElement('command', NS_COMMANDS)
            command_elt['node'] = 'subscribe'
            command_elt['action'] = 'execute'
            command_elt['sessionid'] = session_id
            description = self.host.memory.getParamA(PARAM_NAME_DESC[0], PARAM_CATEGORY[0], profile_key=client.profile)
            ret_form = data_form.Form('submit')
            ret_form.makeFields({'jid': client.jid.userhost(), 'description': description})
            command_elt.addChild(ret_form.toElement())
            yield sub_req.send(self.service.userhost())

    def paramUpdateTrigger(self, name, value, category, type_, profile):
        """
        Reset all the existing chat state entity data associated with this profile after a parameter modification.
        @param name: parameter name
        @param value: "true" to activate the notifications, or any other value to delete it
        @param category: parameter category
        """
        if (category, name) == (PARAM_CATEGORY[0], PARAM_NAME_SUB[0]):
            self.manageSubscription(value.lower()=='true', profile)
            return False
        return True
