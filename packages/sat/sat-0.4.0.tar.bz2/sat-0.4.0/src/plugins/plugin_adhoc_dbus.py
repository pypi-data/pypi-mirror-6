#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for adding D-Bus to Ad-Hoc Commands
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
from twisted.internet import defer, reactor
from wokkel import data_form
from lxml import etree
from os import path
import uuid
import dbus
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

FD_NAME = "org.freedesktop.DBus"
FD_PATH = "/org/freedekstop/DBus"
INTROSPECT_IFACE = "org.freedesktop.DBus.Introspectable"

INTROSPECT_METHOD = "Introspect"
IGNORED_IFACES_START = ('org.freedesktop', 'org.qtproject', 'org.kde.KMainWindow') # commands in interface starting with these values will be ignored
FLAG_LOOP = 'LOOP'

PLUGIN_INFO = {
    "name": "Ad-Hoc Commands - D-Bus",
    "import_name": "AD_HOC_DBUS",
    "type": "Misc",
    "protocols": [],
    "dependencies": ["XEP-0050"],
    "main": "AdHocDBus",
    "handler": "no",
    "description": _("""Add D-Bus management to Ad-Hoc commands""")
}


class AdHocDBus(object):

    def __init__(self, host):
        info(_("plugin Ad-Hoc D-Bus initialization"))
        self.host = host
        host.bridge.addMethod("adHocDBusAddAuto", ".plugin", in_sign='sasasasasasass', out_sign='(sa(sss))',
                              method=self._adHocDBusAddAuto,
                              async=True)
        self.session_bus = dbus.SessionBus()
        self.fd_object = self.session_bus.get_object(FD_NAME, FD_PATH, introspect=False)
        self.XEP_0050 = host.plugins['XEP-0050']

    def _DBusAsyncCall(self, proxy, method, *args, **kwargs):
        """ Call a DBus method asynchronously and return a deferred
        @param proxy: DBus object proxy, as returner by get_object
        @param method: name of the method to call
        @param args: will be transmitted to the method
        @param kwargs: will be transmetted to the method, except for the following poped values:
                       - interface: name of the interface to use
        @return: a deferred

        """
        d = defer.Deferred()
        interface = kwargs.pop('interface', None)
        kwargs['reply_handler'] = lambda ret=None: d.callback(ret)
        kwargs['error_handler'] = d.errback
        proxy.get_dbus_method(method, dbus_interface=interface)(*args, **kwargs)
        return d

    def _DBusListNames(self):
        return self._DBusAsyncCall(self.fd_object, "ListNames")

    def _DBusIntrospect(self, proxy):
        return self._DBusAsyncCall(proxy, INTROSPECT_METHOD, interface=INTROSPECT_IFACE)

    def _acceptMethod(self, method):
        """ Return True if we accept the method for a command
        @param method: etree.Element
        @return: True if the method is acceptable

        """
        if method.xpath("arg[@direction='in']"): # we don't accept method with argument for the moment
            return False
        return True

    @defer.inlineCallbacks
    def _introspect(self, methods, bus_name, proxy):
        debug("introspecting path [%s]" % proxy.object_path)
        introspect_xml = yield self._DBusIntrospect(proxy)
        el = etree.fromstring(introspect_xml)
        for node in el.iterchildren('node', 'interface'):
            if node.tag == 'node':
                new_path = path.join(proxy.object_path, node.get('name'))
                new_proxy = self.session_bus.get_object(bus_name, new_path, introspect=False)
                yield self._introspect(methods, bus_name, new_proxy)
            elif node.tag == 'interface':
                name = node.get('name')
                if any(name.startswith(ignored) for ignored in IGNORED_IFACES_START):
                    debug('interface [%s] is ignored' % name)
                    continue
                debug("introspecting interface [%s]" % name)
                for method in node.iterchildren('method'):
                    if self._acceptMethod(method):
                        method_name = method.get('name')
                        debug("method accepted: [%s]" % method_name)
                        methods.add((proxy.object_path, name, method_name))

    def _adHocDBusAddAuto(self, prog_name, allowed_jids, allowed_groups, allowed_magics, forbidden_jids, forbidden_groups, flags, profile_key):
        return self.adHocDBusAddAuto(prog_name, allowed_jids, allowed_groups, allowed_magics, forbidden_jids, forbidden_groups, flags, profile_key)

    @defer.inlineCallbacks
    def adHocDBusAddAuto(self, prog_name, allowed_jids=None, allowed_groups=None, allowed_magics=None, forbidden_jids=None, forbidden_groups=None, flags=None, profile_key='@NONE@'):
        bus_names = yield self._DBusListNames()
        bus_names = [bus_name for bus_name in bus_names if '.' + prog_name in bus_name]
        if not bus_names:
            info("Can't find any bus for [%s]" % prog_name)
            return
        bus_names.sort()
        for bus_name in bus_names:
            if bus_name.endswith(prog_name):
                break
        info("bus name found: [%s]" % bus_name)
        proxy = self.session_bus.get_object(bus_name, '/', introspect=False)
        methods = set()

        yield self._introspect(methods, bus_name, proxy)

        if methods:
            self._addCommand(prog_name, bus_name, methods,
                             allowed_jids = allowed_jids,
                             allowed_groups = allowed_groups,
                             allowed_magics = allowed_magics,
                             forbidden_jids = forbidden_jids,
                             forbidden_groups = forbidden_groups,
                             flags = flags,
                             profile_key = profile_key)

        defer.returnValue((bus_name, methods))


    def _addCommand(self, adhoc_name, bus_name, methods, allowed_jids=None, allowed_groups=None, allowed_magics=None, forbidden_jids=None, forbidden_groups=None, flags=None, profile_key='@NONE@'):
        if flags is None:
            flags = set()

        def DBusCallback(command_elt, session_data, action, node, profile):
            actions = session_data.setdefault('actions',[])
            names_map = session_data.setdefault('names_map', {})
            actions.append(action)

            if len(actions) == 1:
                # it's our first request, we ask the desired new status
                status = self.XEP_0050.STATUS.EXECUTING
                form = data_form.Form('form', title=_('Command selection'))
                options = []
                for path, iface, command in methods:
                    label = command.rsplit('.',1)[-1]
                    name = str(uuid.uuid4())
                    names_map[name] = (path, iface, command)
                    options.append(data_form.Option(name, label))

                field = data_form.Field('list-single', 'command', options=options, required=True)
                form.addField(field)

                payload = form.toElement()
                note = None

            elif len(actions) == 2:
                # we should have the answer here
                try:
                    x_elt = command_elt.elements(data_form.NS_X_DATA,'x').next()
                    answer_form = data_form.Form.fromElement(x_elt)
                    command = answer_form['command']
                except KeyError, StopIteration:
                    raise self.XEP_0050.AdHocError(self.XEP_0050.ERROR.BAD_PAYLOAD)

                if command not in names_map:
                    raise self.XEP_0050.AdHocError(self.XEP_0050.ERROR.BAD_PAYLOAD)

                path, iface, command = names_map[command]
                proxy = self.session_bus.get_object(bus_name, path)

                d = self._DBusAsyncCall(proxy, command, interface=iface)

                # job done, we can end the session, except if we have FLAG_LOOP
                if FLAG_LOOP in flags:
                    # We have a loop, so we clear everything and we execute again the command as we had a first call (command_elt is not used, so None is OK)
                    del actions[:]
                    names_map.clear()
                    return DBusCallback(None, session_data, self.XEP_0050.ACTION.EXECUTE, node, profile)
                form = data_form.Form('form', title=_(u'Updated'))
                form.addField(data_form.Field('fixed', u'Command sent'))
                status = self.XEP_0050.STATUS.COMPLETED
                payload = None
                note = (self.XEP_0050.NOTE.INFO, _(u"Command sent"))
            else:
                raise self.XEP_0050.AdHocError(self.XEP_0050.ERROR.INTERNAL)

            return (payload, status, None, note)

        self.XEP_0050.addAdHocCommand(DBusCallback, adhoc_name,
                                      allowed_jids = allowed_jids,
                                      allowed_groups = allowed_groups,
                                      allowed_magics = allowed_magics,
                                      forbidden_jids = forbidden_jids,
                                      forbidden_groups = forbidden_groups,
                                      profile_key = profile_key)
