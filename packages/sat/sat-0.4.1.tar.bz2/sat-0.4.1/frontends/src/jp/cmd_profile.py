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

"""This module permits to manage profiles. It can list, create, delete
and retrieve informations about a profile."""

from logging import debug, info, error, warning
from sat.core.i18n import _
from sat_frontends.jp import base
from sat.tools.jid import JID

__commands__ = ["Profile"]

PROFILE_HELP = _('The name of the profile')


class ProfileDelete(base.CommandBase):
    def __init__(self, host):
        super(ProfileDelete, self).__init__(host, 'delete', use_profile=False, help=_('Delete a profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=PROFILE_HELP)

    def run(self):
        super(ProfileDelete, self).run()
        if self.args.profile not in self.host.bridge.getProfilesList():
            error("Profile %s doesn't exist." % self.args.profile)
            self.host.quit(1)
        self.host.bridge.deleteProfile(self.args.profile)


class ProfileInfo(base.CommandBase):
    def __init__(self, host):
        super(ProfileInfo, self).__init__(host, 'info', use_profile=False, help=_('Get informations about a profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=PROFILE_HELP)

    def run(self):
        super(ProfileInfo, self).run()
        self.need_loop = True

        def getPassword(password):
            print "pwd: %s" % password
            self.host.quit()

        def getJID(jid):
            print "jid: %s" % jid
            self.host.bridge.asyncGetParamA("Password", "Connection", profile_key=self.args.profile, callback=getPassword)

        if self.args.profile not in self.host.bridge.getProfilesList():
            error("Profile %s doesn't exist." % self.args.profile)
            self.host.quit(1)

        self.host.bridge.asyncGetParamA("JabberID", "Connection", profile_key=self.args.profile, callback=getJID)


class ProfileList(base.CommandBase):
    def __init__(self, host):
        super(ProfileList, self).__init__(host, 'list', use_profile=False, help=_('List profiles'))

    def add_parser_options(self):
        pass

    def run(self):
        super(ProfileList, self).run()
        for profile in self.host.bridge.getProfilesList():
            print profile


class ProfileCreate(base.CommandBase):
    def __init__(self, host):
        super(ProfileCreate, self).__init__(host, 'create', use_profile=False, help=_('Create a new profile'))

    def add_parser_options(self):
        self.parser.add_argument('profile', type=str, help=_('the name of the profile'))
        self.parser.add_argument('jid', type=str, help=_('the jid of the profile'))
        self.parser.add_argument('password', type=str, help=_('the password of the profile'))

    def _profile_created(self):
        self.host.bridge.setParam("JabberID", self.args.jid, "Connection" ,profile_key=self.args.profile)
        self.host.bridge.setParam("Server", JID(self.args.jid).domain, "Connection", profile_key=self.args.profile)
        self.host.bridge.setParam("Password", self.args.password, "Connection", profile_key=self.args.profile)
        self.host.quit()

    def run(self):
        """Create a new profile"""
        self.need_loop = True
        if self.args.profile in self.host.bridge.getProfilesList():
            error("Profile %s already exists." % self.args.profile)
            self.host.quit(1)
        self.host.bridge.asyncCreateProfile(self.args.profile, self._profile_created, None)


class Profile(base.CommandBase):
    subcommands = (ProfileDelete, ProfileInfo, ProfileList, ProfileCreate)

    def __init__(self, host):
        super(Profile, self).__init__(host, 'profile', use_profile=False, help=_('Profile commands'))
