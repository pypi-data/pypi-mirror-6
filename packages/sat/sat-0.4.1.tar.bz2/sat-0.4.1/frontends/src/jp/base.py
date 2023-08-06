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

from sat.core.i18n import _

global pbar_available
pbar_available = True #checked before using ProgressBar

### logging ###
import logging
from logging import debug, info, error, warning
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s')
###

import sys
import locale
import os.path
import argparse
import gobject
from glob import iglob
from importlib import import_module
from sat.tools.jid import JID
from sat_frontends.bridge.DBus import DBusBridgeFrontend
from sat.core import exceptions
import sat_frontends.jp
try:
    import progressbar
except ImportError:
    info (_('ProgressBar not available, please download it at http://pypi.python.org/pypi/progressbar'))
    info (_('Progress bar deactivated\n--\n'))
    progressbar=None

#consts
prog_name = u"jp"
description = """This software is a command line tool for XMPP.
Get the latest version at http://sat.goffi.org"""

copyleft = u"""Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson (aka Goffi)
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it under certain conditions.
"""


def unicode_decoder(arg):
    # Needed to have unicode strings from arguments
    return arg.decode(locale.getpreferredencoding())


class Jp(object):
    """
    This class can be use to establish a connection with the
    bridge. Moreover, it should manage a main loop.

    To use it, you mainly have to redefine the method run to perform
    specify what kind of operation you want to perform.

    """
    def __init__(self):
        try:
            self.bridge = DBusBridgeFrontend()
        except exceptions.BridgeExceptionNoService:
            print(_(u"Can't connect to SàT backend, are you sure it's launched ?"))
            sys.exit(1)
        except exceptions.BridgeInitError:
            print(_(u"Can't init bridge"))
            sys.exit(1)

        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                              description=description)

        self._make_parents()
        self.add_parser_options()
        self.subparsers = self.parser.add_subparsers(title=_('Available commands'), dest='subparser_name')
        self._auto_loop = False # when loop is used for internal reasons
        self.need_loop = False # to set by commands when loop is needed
        self._progress_id = None # TODO: manage several progress ids
        self.quit_on_progress_end = True # set to False if you manage yourself exiting, or if you want the user to stop by himself

    @property
    def version(self):
        return self.bridge.getVersion()

    @property
    def progress_id(self):
        return self._progress_id

    @progress_id.setter
    def progress_id(self, value):
        self._progress_id = value

    def _make_parents(self):
        self.parents = {}

        profile_parent = self.parents['profile'] = argparse.ArgumentParser(add_help=False)
        profile_parent.add_argument("-p", "--profile", action="store", type=str, default='@DEFAULT@', help=_("Use PROFILE profile key (default: %(default)s)"))
        profile_parent.add_argument("-c", "--connect", action="store_true", help=_("Connect the profile before doing anything else"))

        progress_parent = self.parents['progress'] = argparse.ArgumentParser(add_help=False)
        if progressbar:
            progress_parent.add_argument("-P", "--progress", action="store_true", help=_("Show progress bar"))

    def add_parser_options(self):
        self.parser.add_argument('--version', action='version', version=("%(name)s %(version)s %(copyleft)s" % {'name': prog_name, 'version': self.version, 'copyleft': copyleft}))

    def import_commands(self):
        """ Automaticaly import commands to jp
        looks from modules names cmd_*.py in jp path and import them

        """
        path = os.path.dirname(sat_frontends.jp.__file__)
        modules = (os.path.splitext(module)[0] for module in map(os.path.basename, iglob(os.path.join(path, "cmd_*.py"))))
        for module_name in modules:
            module = import_module("sat_frontends.jp."+module_name)
            try:
                self.import_command_module(module)
            except ImportError:
                continue

    def import_command_module(self, module):
        """ Add commands from a module to jp
        @param module: module containing commands

        """
        try:
            for classname in module.__commands__:
                cls = getattr(module, classname)
        except AttributeError:
            warning(_("Invalid module %s") % module)
            raise ImportError
        cls(self)


    def run(self, args=None):
        self.args = self.parser.parse_args(args)
        self.args.func()
        if self.need_loop or self._auto_loop:
            self._start_loop()

    def _start_loop(self):
        self.loop = gobject.MainLoop()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            info(_("User interruption: good bye"))

    def stop_loop(self):
        try:
            self.loop.quit()
        except AttributeError:
            pass

    def quit(self, errcode=0):
        self.stop_loop()
        if errcode:
            sys.exit(errcode)

    def check_jids(self, jids):
        """Check jids validity, transform roster name to corresponding jids

        @param profile: profile name
        @param jids: list of jids
        @return: List of jids

        """
        names2jid = {}
        nodes2jid = {}

        for contact in self.bridge.getContacts(self.profile):
            _jid, attr, groups = contact
            if attr.has_key("name"):
                names2jid[attr["name"].lower()] = _jid
            nodes2jid[JID(_jid).node.lower()] = _jid

        def expand_jid(jid):
            _jid = jid.lower()
            if _jid in names2jid:
                expanded = names2jid[_jid]
            elif _jid in nodes2jid:
                expanded = nodes2jid[_jid]
            else:
                expanded = jid
            return unicode(expanded)

        def check(jid):
            if not jid.is_valid:
                error (_("%s is not a valid JID !"), jid)
                self.quit(1)

        dest_jids=[]
        try:
            for i in range(len(jids)):
                dest_jids.append(expand_jid(jids[i]))
                check(dest_jids[i])
        except AttributeError:
            pass

        return dest_jids

    def connect_profile(self, callback):
        """ Check if the profile is connected
        @param callback: method to call when profile is connected
        @exit: - 1 when profile is not connected and --connect is not set
               - 1 when the profile doesn't exists
               - 1 when there is a connection error
        """
        # FIXME: need better exit codes

        def cant_connect():
            error(_(u"Can't connect profile"))
            self.quit(1)

        self.profile = self.bridge.getProfileName(self.args.profile)

        if not self.profile:
            error(_("The profile [%s] doesn't exist") % self.args.profile)
            self.quit(1)

        if self.args.connect: #if connection is asked, we connect the profile
            self.bridge.asyncConnect(self.profile, callback, cant_connect)
            self._auto_loop = True
            return

        elif not self.bridge.isConnected(self.profile):
            error(_(u"Profile [%(profile)s] is not connected, please connect it before using jp, or use --connect option") % { "profile": self.profile })
            self.quit(1)

        callback()

    def get_full_jid(self, param_jid):
        """Return the full jid if possible (add last resource when find a bare jid)"""
        _jid = JID(param_jid)
        if not _jid.resource:
            #if the resource is not given, we try to add the last known resource
            last_resource = self.bridge.getLastResource(param_jid, self.profile)
            if last_resource:
                return "%s/%s" % (_jid.bare, last_resource)
        return param_jid

    def watch_progress(self):
        self.pbar = None
        gobject.timeout_add(10, self._progress_cb)

    def _progress_cb(self):
        if self.progress_id:
            data = self.bridge.getProgress(self.progress_id, self.profile)
            if data:
                if not data['position']:
                    data['position'] = '0'
                if not self.pbar:
                    #first answer, we must construct the bar
                    self.pbar = progressbar.ProgressBar(int(data['size']),
                                                        [_("Progress: "),progressbar.Percentage(),
                                                         " ",
                                                         progressbar.Bar(),
                                                         " ",
                                                         progressbar.FileTransferSpeed(),
                                                         " ",
                                                         progressbar.ETA()])
                    self.pbar.start()

                self.pbar.update(int(data['position']))

            elif self.pbar:
                self.pbar.finish()
                if self.quit_on_progress_end:
                    self.quit()
                return False

        return True


class CommandBase(object):

    def __init__(self, host, name, use_profile=True, use_progress=False, help=None, **kwargs):
        """ Initialise CommandBase
        @param host: Jp instance
        @param name: name of the new command
        @param use_profile: if True, add profile selection/connection commands
        @param use_progress: if True, add progress bar activation commands
        @param help: help message to display
        @param **kwargs: args passed to ArgumentParser

        """
        try: # If we have subcommands, host is a CommandBase and we need to use host.host
            self.host = host.host
        except AttributeError:
            self.host = host

        parents = kwargs.setdefault('parents', set())
        if use_profile:
            #self.host.parents['profile'] is an ArgumentParser with profile connection arguments
            parents.add(self.host.parents['profile'])
        if use_progress:
            parents.add(self.host.parents['progress'])

        self.parser = host.subparsers.add_parser(name, help=help, **kwargs)
        if hasattr(self, "subcommands"):
            self.subparsers = self.parser.add_subparsers()
        else:
            self.parser.set_defaults(func=self.run)
        self.add_parser_options()

    @property
    def args(self):
        return self.host.args

    @property
    def need_loop(self):
        return self.host.need_loop

    @need_loop.setter
    def need_loop(self, value):
        self.host.need_loop = value

    @property
    def profile(self):
        return self.host.profile

    @property
    def progress_id(self):
        return self.host.progress_id

    @progress_id.setter
    def progress_id(self, value):
        self.host.progress_id = value

    def add_parser_options(self):
        try:
            subcommands = self.subcommands
        except AttributeError:
            # We don't have subcommands, the class need to implements add_parser_options
            raise NotImplementedError

        # now we add subcommands to ourself
        for cls in subcommands:
            cls(self)

    def run(self):
        try:
            if self.args.profile:
                self.host.connect_profile(self.connected)
        except AttributeError:
            # the command doesn't need to connect profile
            pass
        try:
            if self.args.progress:
                self.host.watch_progress()
        except AttributeError:
            # the command doesn't use progress bar
            pass

    def connected(self):
        if not self.need_loop:
            self.host.stop_loop()


class CommandAnswering(CommandBase):
    #FIXME: temp, will be refactored when progress_bar/confirmations will be refactored

    def _ask_confirmation(self, confirm_id, confirm_type, data, profile):
        """ Callback used for file transfer, accept files depending on parameters"""
        if profile != self.profile:
            debug("Ask confirmation ignored: not our profile")
            return
        if confirm_type == self.confirm_type:
            if self.dest_jids and not JID(data['from']).bare in [JID(_jid).bare for _jid in self.dest_jids()]:
                return #file is not sent by a filtered jid
            else:
                self.ask(data, confirm_id)

    def ask(self):
        """
        The return value is used to answer to the bridge.
        @return: bool or dict
        """
        raise NotImplementedError

    def connected(self):
        """Auto reply to confirmations requests"""
        self.need_loop = True
        super(CommandAnswering, self).connected()
        # we watch confirmation signals
        self.host.bridge.register("ask_confirmation", self._ask_confirmation)

        #and we ask those we have missed
        for confirm_id, confirm_type, data in self.host.bridge.getWaitingConf(self.profile):
            self._ask_confirmation(confirm_id, confirm_type, data, self.profile)
