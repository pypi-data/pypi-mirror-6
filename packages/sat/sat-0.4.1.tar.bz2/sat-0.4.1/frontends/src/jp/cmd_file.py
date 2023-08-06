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
import os.path
import tarfile
from sat.core.i18n import _

__commands__ = ["File"]

class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(host, 'send', use_progress=True, help=_('Send a file to a contact'))

    def add_parser_options(self):
        self.parser.add_argument("files", type=str, nargs = '+', help=_("A list of file"))
        self.parser.add_argument("jid", type=base.unicode_decoder, help=_("The destination jid"))
        self.parser.add_argument("-b", "--bz2", action="store_true", help=_("Make a bzip2 tarball"))

    def connected(self):
        """Send files to jabber contact"""
        self.need_loop=True
        super(Send, self).connected()
        self.send_files()

    def send_files(self):

        for file_ in self.args.files:
            if not os.path.exists(file_):
                error (_(u"file [%s] doesn't exist !") % file_)
                self.host.quit(1)
            if not self.args.bz2 and os.path.isdir(file_):
                error (_("[%s] is a dir ! Please send files inside or use compression") % file_)
                self.host.quit(1)

        full_dest_jid = self.host.get_full_jid(self.args.jid)

        if self.args.bz2:
            tmpfile = (os.path.basename(self.args.files[0]) or os.path.basename(os.path.dirname(self.args.files[0])) ) + '.tar.bz2' #FIXME: tmp, need an algorithm to find a good name/path
            if os.path.exists(tmpfile):
                error (_("tmp file_ (%s) already exists ! Please remove it"), tmpfile)
                exit(1)
            warning(_("bz2 is an experimental option at an early dev stage, use with caution"))
            #FIXME: check free space, writting perm, tmp dir, filename (watch for OS used)
            print _(u"Starting compression, please wait...")
            sys.stdout.flush()
            bz2 = tarfile.open(tmpfile, "w:bz2")
            for file_ in self.args.files:
                print _(u"Adding %s") % file_
                bz2.add(file_)
            bz2.close()
            print _(u"Done !")
            path = os.path.abspath(tmpfile)
            self.progress_id = self.host.bridge.sendFile(full_dest_jid, path, {}, self.profile)
        else:
            for file_ in self.args.files:
                path = os.path.abspath(file_)
                self.progress_id = self.host.bridge.sendFile(full_dest_jid, path, {}, self.profile) #FIXME: show progress only for last progress_id


class Receive(base.CommandAnswering):
    confirm_type = "FILE_TRANSFER"

    def __init__(self, host):
        super(Receive, self).__init__(host, 'recv', use_progress=True, help=_('Wait for a file to be sent by a contact'))

    @property
    def dest_jids(self):
        return self.args.jids

    def add_parser_options(self):
        self.parser.add_argument("jids", type=base.unicode_decoder, nargs="*", help=_('Jids accepted (none means "accept everything")'))
        self.parser.add_argument("-m", "--multiple", action="store_true", help=_("Accept multiple files (you'll have to stop manually)"))
        self.parser.add_argument("-f", "--force", action="store_true", help=_("Force overwritting of existing files"))


    def ask(self, data, confirm_id):
        answer_data = {}
        answer_data["dest_path"] = os.path.join(os.getcwd(), data['filename'])

        if self.args.force or not os.path.exists(answer_data["dest_path"]):
            self.host.bridge.confirmationAnswer(confirm_id, True, answer_data, self.profile)
            info(_("Accepted file [%(filename)s] from %(sender)s") % {'filename':data['filename'], 'sender':data['from']})
            self.progress_id = confirm_id
        else:
            self.host.bridge.confirmationAnswer(confirm_id, False, answer_data, self.profile)
            warning(_("Refused file [%(filename)s] from %(sender)s: a file with the same name already exist") % {'filename':data['filename'], 'sender':data['from']})
            if not self.args.multiple:
                self.host.quit()

        if not self.args.multiple and not self.args.progress:
            #we just accept one file
            self.host.quit()

    def run(self):
        super(Receive, self).run()
        if self.args.multiple:
            self.host.quit_on_progress_end = False


class File(base.CommandBase):
    subcommands = (Send, Receive)

    def __init__(self, host):
        super(File, self).__init__(host, 'file', use_profile=False, help=_('File sending/receiving'))
