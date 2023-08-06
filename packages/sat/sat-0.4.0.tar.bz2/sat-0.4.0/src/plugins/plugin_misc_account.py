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

from sat.core.i18n import _
from logging import debug, info, warning, error
from sat.core import exceptions
from twisted.internet import reactor, defer, protocol
from os.path import join, dirname
from twisted.python.procutils import which
from twisted.python.failure import Failure
from email.mime.text import MIMEText
from twisted.mail.smtp import sendmail

PLUGIN_INFO = {
    "name": "Account Plugin",
    "import_name": "MISC-ACCOUNT",
    "type": "MISC",
    "protocols": [],
    "dependencies": [],
    "main": "MiscAccount",
    "handler": "no",
    "description": _(u"""SàT account creation""")
}

CONFIG_SECTION = "plugin account"

# You need do adapt the following consts to your server
# all theses values (key=option name, value=default) can (and should) be overriden in sat.conf
# in section CONFIG_SECTION

default_conf = {"email_from": "NOREPLY@example.net",
                "email_server": "localhost",
                "admin_email": "admin@example.net",
                "new_account_server": "localhost",
                "new_account_domain": "example.net",
                "new_account_resource": "libervia",
                "prosody_path": None, # prosody path (where prosodyctl will be executed from), or None to automaticaly find it
                "prosodyctl": "prosodyctl",
                "reserved_list": ['libervia'] # profiles which can't be used
               }


class ProsodyRegisterProtocol(protocol.ProcessProtocol):
    """ Try to register an account with prosody """

    def __init__(self, password, deferred=None):
        self.password = password
        self.deferred = deferred
        self.data = ''

    def connectionMade(self):
        self.transport.write("%s\n%s" % ((self.password.encode('utf-8'), ) * 2))
        self.transport.closeStdin()

    def outReceived(self, data):
        self.data += data

    def errReceived(self, data):
        self.data += data

    def processEnded(self, reason):
        if (reason.value.exitCode == 0):
            info(_('Prosody registration success'))
            self.deferred.callback(None)
        else:
            error(_(u"Can't register Prosody account (error code: %(code)d): %(message)s") % {'code': reason.value.exitCode, 'message': self.data})
            self.deferred.errback(Failure(exceptions.InternalError))


class MiscAccount(object):
    """Account plugin: create a SàT + Prosody account, used by Libervia"""
    #XXX: This plugin is a Q&D one used for the demo. Something more generic (and not
    #     only focused on Prosody) is planed

    def __init__(self, host):
        info(_(u"Plugin Account initialization"))
        self.host = host
        host.bridge.addMethod("registerSatAccount", ".plugin", in_sign='sss', out_sign='', method=self._registerAccount, async=True)
        host.bridge.addMethod("getNewAccountDomain", ".plugin", in_sign='', out_sign='s', method=self._getNewAccountDomain, async=False)
        self._prosody_path = self.getConfig('prosody_path')
        if self._prosody_path is None:
            paths = which(self.getConfig('prosodyctl'))
            if not paths:
                error(_("Can't find %s") % (self.getConfig('prosodyctl'), ))
            else:
                self._prosody_path = dirname(paths[0])
                info(_('Prosody path found: %s') % (self._prosody_path, ))

    def getConfig(self, name):
        return self.host.memory.getConfig(CONFIG_SECTION, name) or default_conf[name]

    def _registerAccount(self, email, password, profile):

        """
        #Password Generation
        #_charset = [chr(i) for i in range(0x21,0x7F)] #XXX: this charset seems to have some issues with openfire
        _charset = [chr(i) for i in range(0x30,0x3A) + range(0x41,0x5B) + range (0x61,0x7B)]
        import random
        random.seed()
        password = ''.join([random.choice(_charset) for i in range(15)])
        """
        if not email or not password or not profile:
            raise exceptions.DataError

        if profile.lower() in self.getConfig('reserved_list'):
            return defer.fail(Failure(exceptions.ConflictError))

        d = self.host.memory.asyncCreateProfile(profile)
        d.addCallback(self._profileRegistered, email, password, profile)
        return d

    def _profileRegistered(self, result, email, password, profile):

        #FIXME: values must be in a config file instead of hardcoded
        self.host.memory.setParam("JabberID", "%s@%s/%s" % (profile, self.getConfig('new_account_domain'), self.getConfig('new_account_resource')),
                                  "Connection", profile_key=profile)
        self.host.memory.setParam("Server", self.getConfig('new_account_server'),
                                  "Connection", profile_key=profile)
        self.host.memory.setParam("Password", password,
                                  "Connection", profile_key=profile)
        #and the account

        #XXX: we use "prosodyctl adduser" because "register" doesn't check conflict
        #     and just change the password if the account already exists
        d = defer.Deferred()
        prosody_reg = ProsodyRegisterProtocol(password, d)
        prosody_exe = join(self._prosody_path, self.getConfig('prosodyctl'))
        reactor.spawnProcess(prosody_reg, prosody_exe, [prosody_exe, 'adduser', "%s@%s" % (profile, self.getConfig('new_account_domain'))], path=self._prosody_path)

        d.addCallback(self._sendEmails, profile, email, password)
        d.addCallback(lambda ignore: None)
        return d

    def _sendEmails(self, result, login, email, password):
        #time to send the email

        _email_host = self.getConfig('email_server')
        _email_from = self.getConfig("email_from")

        def email_ok(ignore):
            print ("Account creation email sent to %s" % email)

        def email_ko(ignore):
            #TODO: return error code to user
            error("Failed to send email to %s" % email)

        body = (u"""Welcome to Libervia, a Salut à Toi project part

/!\\ WARNING, THIS IS ONLY A TECHNICAL DEMO, DON'T USE THIS ACCOUNT FOR ANY SERIOUS PURPOSE /!\\

Here are your connection informations:
---
login: %(login)s
password: %(password)s

Your Jabber ID (JID) is: %(jid)s
---

To try with some contacts, you can use the directory: subscribe in your parameters, and use it with the Communication/Search directory menu.

SàT website: http://www.salut-a-toi.org
follow SàT news: http://www.goffi.org

Any feedback welcome

Cheers
SàT team""" % {'login': login, 'password': password, 'jid': "%s@%s" % (login, self.getConfig('new_account_domain'))}).encode('utf-8')
        msg = MIMEText(body, 'plain', 'UTF-8')
        msg['Subject'] = 'Libervia account created'
        msg['From'] = _email_from
        msg['To'] = email

        d_user = sendmail(_email_host, _email_from, email, msg.as_string())
        d_user.addCallbacks(email_ok, email_ko)

        #email to the administrator
        body = (u"""New account created: %(login)s [%(email)s]""" % {'login': login, 'email': email}).encode('utf-8')
        msg = MIMEText(body, 'plain', 'UTF-8')
        msg['Subject'] = 'Libervia new account created'
        msg['From'] = _email_from
        msg['To'] = self.getConfig('admin_email')

        d_admin = sendmail(_email_host, _email_from, self.getConfig('admin_email'), msg.as_string())
        d_admin.addCallbacks(email_ok, email_ko)
        return defer.DeferredList([d_user, d_admin])

    def _getNewAccountDomain(self):
        """@return: the domain that will be set to new account"""
        return self.getConfig('new_account_domain')

