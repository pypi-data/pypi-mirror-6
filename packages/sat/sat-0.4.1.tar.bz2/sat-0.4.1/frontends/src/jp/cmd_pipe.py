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

from sat_frontends.jp import base

import tempfile
import sys
import os
import os.path
import shutil
from sat.core.i18n import _

__commands__ = ["Pipe"]

class PipeOut(base.CommandBase):

    def __init__(self, host):
        super(PipeOut, self).__init__(host, 'out', help=_('Pipe a stream out'))

    def add_parser_options(self):
        self.parser.add_argument("jid", type=base.unicode_decoder, help=_("The destination jid"))

    def pipe_out(self):
        """ Create named pipe, and send stdin to it """
        tmp_dir = tempfile.mkdtemp()
        fifopath = os.path.join(tmp_dir,"pipe_out")
        os.mkfifo(fifopath)
        self.host.bridge.pipeOut(self.host.get_full_jid(self.args.jid), fifopath, {}, self.profile)
        with open(fifopath, 'w') as f:
            shutil.copyfileobj(sys.stdin, f)
        shutil.rmtree(tmp_dir)
        self.host.quit()

    def connected(self):
        # TODO: check_jids
        self.need_loop = True
        super(PipeOut, self).connected()
        self.pipe_out()


class PipeIn(base.CommandAnswering):
    confirm_type = "PIPE_TRANSFER"

    def __init__(self, host):
        super(PipeIn, self).__init__(host, 'in', help=_('Wait for the reception of a pipe stream'))

    @property
    def dest_jids(self):
        return self.args.jids

    def add_parser_options(self):
        self.parser.add_argument("jids", type=base.unicode_decoder, nargs="*", help=_('Jids accepted (none means "accept everything")'))

    def ask(self, data, confirm_id):
        answer_data = {}
        tmp_dir = tempfile.mkdtemp()
        fifopath = os.path.join(tmp_dir,"pipe_in")
        answer_data["dest_path"] = fifopath
        os.mkfifo(fifopath)
        self.host.bridge.confirmationAnswer(confirm_id, True, answer_data, self.profile)
        with open(fifopath, 'r') as f:
            shutil.copyfileobj(f, sys.stdout)
        shutil.rmtree(tmp_dir)
        self.host.quit()


class Pipe(base.CommandBase):
    subcommands = (PipeOut, PipeIn)

    def __init__(self, host):
        super(Pipe, self).__init__(host, 'pipe', use_profile=False, help=_('Stream piping through XMPP'))
