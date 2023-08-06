#! /usr/bin/python
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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

from logging import debug, info, error, warning

import base
import sys
import os
from sat.core.i18n import _

__commands__ = ["AdHoc"]

FLAG_LOOP = 'LOOP'
MAGIC_BAREJID = '@PROFILE_BAREJID@'

class Remote(base.CommandBase):
    def __init__(self, host):
        super(Remote, self).__init__(host, 'remote', help=_('Remote control a software'))

    def add_parser_options(self):
        self.parser.add_argument("software", type=str, help=_("Software name"))
        self.parser.add_argument("-j", "--jids", type=base.unicode_decoder, nargs='*', default=[], help=_("Jids allowed to use the command"))
        self.parser.add_argument("-g", "--groups", type=base.unicode_decoder, nargs='*', default=[], help=_("Groups allowed to use the command"))
        self.parser.add_argument("--forbidden-groups", type=base.unicode_decoder, nargs='*', default=[], help=_("Groups that are *NOT* allowed to use the command"))
        self.parser.add_argument("--forbidden-jids", type=base.unicode_decoder, nargs='*', default=[], help=_("Jids that are *NOT* allowed to use the command"))
        self.parser.add_argument("-l", "--loop", action="store_true", help=_("Loop on the commands"))

    def connected(self):
        super(Remote, self).connected()
        name = self.args.software.lower()
        flags = []
        magics = {jid for jid in self.args.jids if jid.count('@')>1}
        magics.add(MAGIC_BAREJID)
        jids = set(self.args.jids).difference(magics)
        if self.args.loop:
            flags.append(FLAG_LOOP)
        bus_name, methods = self.host.bridge.adHocDBusAddAuto(name, jids, self.args.groups, magics,
                                                              self.args.forbidden_jids, self.args.forbidden_groups,
                                                              flags, self.profile)
        debug(_("Bus name found: [%s]" % bus_name))
        for method in methods:
            path, iface, command = method
            debug (_("Command found: (path:%(path)s, iface: %(iface)s) [%(command)s]" % {'path': path,
                                                                                         'iface': iface,
                                                                                         'command': command
                                                                                         }))

class AdHoc(base.CommandBase):
    subcommands = (Remote,)

    def __init__(self, host):
        super(AdHoc, self).__init__(host, 'ad-hoc', use_profile=False, help=_('Ad-hoc commands'))
