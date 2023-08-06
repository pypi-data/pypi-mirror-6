#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin to export commands (experimental)
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
from twisted.internet import reactor, protocol

from sat.tools.misc import SkipOtherTriggers
from sat.tools.utils import clean_ustr

PLUGIN_INFO = {
    "name": "Command export plugin",
    "import_name": "EXP-COMMANS-EXPORT",
    "type": "EXP",
    "protocols": [],
    "dependencies": [],
    "main": "CommandExport",
    "handler": "no",
    "description": _("""Implementation of command export""")
}

class ExportCommandProtocol(protocol.ProcessProtocol):
    """ Try to register an account with prosody """

    def __init__(self, parent, target, options, profile):
        self.parent = parent
        self.target = target
        self.options = options
        self.profile = profile

    def _clean(self, data):
        if not data:
            error ("data should not be empty !")
            return u""
        decoded = data.decode('utf-8', 'ignore')[:-1 if data[-1] == '\n' else None]
        return clean_ustr(decoded)

    def connectionMade(self):
        info("connectionMade :)")

    def outReceived(self, data):
        self.parent.host.sendMessage(self.target, self._clean(data), no_trigger=True, profile_key=self.profile) 

    def errReceived(self, data):
        self.parent.host.sendMessage(self.target, self._clean(data), no_trigger=True, profile_key=self.profile) 

    def processEnded(self, reason):
        info (u"process finished: %d" % (reason.value.exitCode,))
        self.parent.removeProcess(self.target, self)

    def write(self, message):
        self.transport.write(message.encode('utf-8'))

    def boolOption(self, key):
        """ Get boolean value from options
        @param key: name of the option
        @return: True if key exists and set to "true" (case insensitive),
                 False in all other cases """
        value = self.options.get(key, "")
        return value.lower() == "true"


class CommandExport(object):
    """Command export plugin: export a command to an entity"""
    #XXX: This plugin can be potentially dangerous if we don't trust entities linked
    #     this is specially true if we have other triggers.

    def __init__(self, host):
        info(_("Plugin command export initialization"))
        self.host = host
        self.spawned = {} # key = entity
        host.trigger.add("MessageReceived", self.MessageReceivedTrigger, priority=10000)
        host.bridge.addMethod("exportCommand", ".plugin", in_sign='sasasa{ss}s', out_sign='', method=self._exportCommand)

    def removeProcess(self, entity, process):
        """ Called when the process is finished
        @param entity: jid.JID attached to the process
        @param process: process to remove"""
        try:
            processes_set = self.spawned[(entity, process.profile)]
            processes_set.discard(process)
            if not processes_set:
                del(self.spawned[(entity, process.profile)])
        except ValueError:
            pass

    def MessageReceivedTrigger(self, message, post_treat, profile):
        """ Check if source is linked and repeat message, else do nothing  """
        from_jid = jid.JID(message["from"])
        spawned_key = (from_jid.userhostJID(), profile)
        try:
            body = [e for e in message.elements() if e.name == 'body'][0]
        except IndexError:
            # do not block message without body (chat state notification...)
            warning("No body element found in message, following normal behaviour")
            return True

        mess_data = unicode(body) + '\n'

        if spawned_key in self.spawned:
            processes_set = self.spawned[spawned_key]
            _continue = False
            exclusive = False
            for process in processes_set:
                process.write(mess_data)
                _continue &= process.boolOption("continue")
                exclusive |= process.boolOption("exclusive")
            if exclusive:
                raise SkipOtherTriggers
            return _continue

        return True

    def _exportCommand(self, command, args, targets, options, profile_key):
        """ Export a commands to authorised targets
        @param command: full path of the command to execute
        @param args: list of arguments, with command name as first one
        @param targets: list of allowed entities
        @param options: export options, a dict which can have the following keys ("true" to set booleans):
                        - exclusive: if set, skip all other triggers
                        - loop: if set, restart the command once terminated #TODO
                        - pty: if set, launch in a pseudo terminal
                        - continue: continue normal MessageReceived handling
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            warning("Unknown profile [%s]" % (profile,))
            return
        
        for target in targets:
            try:
                _jid = jid.JID(target)
                if not _jid.user or not _jid.host:
                    raise jid.InvalidFormat
                _jid = _jid.userhostJID()
            except (jid.InvalidFormat, RuntimeError):
                info(u"invalid target ignored: %s" % (target,))
                continue
            process_prot = ExportCommandProtocol(self, _jid, options, profile)
            self.spawned.setdefault((_jid, profile),set()).add(process_prot)
            reactor.spawnProcess(process_prot, command, args, usePTY = process_prot.boolOption('pty'))

