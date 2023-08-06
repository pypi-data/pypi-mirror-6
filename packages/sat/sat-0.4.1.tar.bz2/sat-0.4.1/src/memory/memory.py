#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

from __future__ import with_statement
from sat.core.i18n import _

import os.path
import csv
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError
from xml.dom import minidom
from uuid import uuid4
from logging import debug, info, warning, error
from twisted.internet import defer, reactor
from twisted.words.protocols.jabber import jid
from twisted.python.failure import Failure
from sat.tools.xml_tools import paramsXML2XMLUI
from sat.core.default_config import default_config
from sat.memory.sqlite import SqliteStorage
from sat.memory.persistent import PersistentDict
from sat.core import exceptions

SAVEFILE_DATABASE = "/sat.db"
NO_SECURITY_LIMIT = -1
INDIVIDUAL = "individual"
GENERAL = "general"


class Sessions(object):
    DEFAULT_TIMEOUT = 600

    def __init__(self, timeout = None):
        """
        @param timeout: nb of seconds before session destruction
        """
        self._sessions = dict()
        self.timeout = timeout or Sessions.DEFAULT_TIMEOUT

    def newSession(self, session_data=None, profile=None):
        """ Create a new session
        @param session_data: mutable data to use, default to a dict
        @param profile: if set, the session is owned by the profile,
                        and profileGet must be used instead of __getitem__
        @return: session_id, session_data
        """
        session_id = str(uuid4())
        timer = reactor.callLater(self.timeout, self._purgeSession, session_id)
        if session_data is None:
            session_data = {}
        self._sessions[session_id] = (timer, session_data) if profile is None else (timer, session_data, profile)
        return session_id, session_data

    def _purgeSession(self, session_id):
        del self._sessions[session_id]
        debug("Session [%s] purged" % session_id)

    def __len__(self):
        return len(self._sessions)

    def __contains__(self, session_id):
        return session_id in self._sessions

    def profileGet(self, session_id, profile):
        try:
            timer, session_data, profile_set = self._sessions[session_id]
        except ValueError:
            raise exceptions.InternalError("You need to use __getitem__ when profile is not set")
        if profile_set != profile:
            raise exceptions.InternalError("current profile differ from set profile !")
        timer.reset(self.timeout)
        return session_data

    def __getitem__(self, session_id):
        try:
            timer, session_data = self._sessions[session_id]
        except ValueError:
            raise exceptions.InternalError("You need to use profileGet instead of __getitem__ when profile is set")
        timer.reset(self.timeout)
        return session_data

    def __setitem__(self, key, value):
        raise NotImplementedError("You need do use newSession to create a session")

    def __delitem__(self, session_id):
        """ Cancel the timer, then actually delete the session data """
        try:
            timer = self._sessions[session_id][0]
            timer.cancel()
            self._purgeSession(session_id)
        except KeyError:
            debug ("Session [%s] doesn't exists, timeout expired ?" % session_id)

    def keys(self):
        return self._sessions.keys()

    def iterkeys(self):
        return self._sessions.iterkeys()


class Params(object):
    """This class manage parameters with xml"""
    ### TODO: add desciption in params

    #TODO: move Watched in a plugin
    #TODO: when priority is changed, a new presence stanza must be emitted
    #TODO: int type (Priority should be int instead of string)
    default_xml = u"""
    <params>
    <general>
    </general>
    <individual>
        <category name="Connection" label="%(category_connection)s">
            <param name="JabberID" value="name@example.org/SàT" type="string" />
            <param name="Password" value="" type="password" />
            <param name="Priority" value="50" type="string" />
            <param name="Server" value="example.org" type="string" />
            <param name="Port" value="5222" type="string" />
            <param name="NewAccount" label="%(label_NewAccount)s" type="button" callback_id="registerNewAccount"/>
            <param name="autoconnect" label="%(label_autoconnect)s" value="true" type="bool" />
            <param name="autodisconnect" label="%(label_autodisconnect)s" value="false"  type="bool" />
        </category>
        <category name="Misc" label="%(category_misc)s">
            <param name="Watched" value="test@Jabber.goffi.int" type="string" />
        </category>
    </individual>
    </params>
    """ % {
        'category_connection': _("Connection"),
        'label_NewAccount': _("Register new account"),
        'label_autoconnect': _('Connect on frontend startup'),
        'label_autodisconnect': _('Disconnect on frontend closure'),
        'category_misc': _("Misc")
    }

    def load_default_params(self):
        self.dom = minidom.parseString(Params.default_xml.encode('utf-8'))

    def _mergeParams(self, source_node, dest_node):
        """Look for every node in source_node and recursively copy them to dest if they don't exists"""

        def getNodesMap(children):
            ret = {}
            for child in children:
                if child.nodeType == child.ELEMENT_NODE:
                    ret[(child.tagName, child.getAttribute('name'))] = child
            return ret
        source_map = getNodesMap(source_node.childNodes)
        dest_map = getNodesMap(dest_node.childNodes)
        source_set = set(source_map.keys())
        dest_set = set(dest_map.keys())
        to_add = source_set.difference(dest_set)

        for node_key in to_add:
            dest_node.appendChild(source_map[node_key].cloneNode(True))

        to_recurse = source_set - to_add
        for node_key in to_recurse:
            self._mergeParams(source_map[node_key], dest_map[node_key])

    def load_xml(self, xml_file):
        """Load parameters template from file"""
        self.dom = minidom.parse(xml_file)
        default_dom = minidom.parseString(Params.default_xml.encode('utf-8'))
        self._mergeParams(default_dom.documentElement, self.dom.documentElement)

    def loadGenParams(self):
        """Load general parameters data from storage
        @return: deferred triggered once params are loaded"""
        return self.storage.loadGenParams(self.params_gen)

    def loadIndParams(self, profile, cache=None):
        """Load individual parameters
        set self.params cache or a temporary cache
        @param profile: profile to load (*must exist*)
        @param cache: if not None, will be used to store the value, as a short time cache
        @return: deferred triggered once params are loaded"""
        if cache is None:
            self.params[profile] = {}
        return self.storage.loadIndParams(self.params[profile] if cache is None else cache, profile)

    def purgeProfile(self, profile):
        """Remove cache data of a profile
        @param profile: %(doc_profile)s"""
        try:
            del self.params[profile]
        except KeyError:
            error(_("Trying to purge cache of a profile not in memory: [%s]") % profile)

    def save_xml(self, filename):
        """Save parameters template to xml file"""
        with open(filename, 'wb') as xml_file:
            xml_file.write(self.dom.toxml('utf-8'))

    def __init__(self, host, storage):
        debug("Parameters init")
        self.host = host
        self.storage = storage
        self.default_profile = None
        self.params = {}
        self.params_gen = {}
        host.registerCallback(host.registerNewAccountCB, with_data=True, force_id="registerNewAccount")

    def createProfile(self, profile):
        """Create a new profile
        @param profile: profile of the profile"""
        #FIXME: must be asynchronous and call the callback once the profile actually exists
        if self.storage.hasProfile(profile):
            info(_('The profile [%s] already exists') % (profile, ))
            return True
        if not self.host.trigger.point("ProfileCreation", profile):
            return False
        self.storage.createProfile(profile)
        return False

    def asyncCreateProfile(self, profile):
        """Create a new profile
        @param profile: name of the profile
        @param callback: called when the profile actually exists in database and memory
        @param errback: called with a string constant as parameter:
                        - CONFLICT: the profile already exists
                        - CANCELED: profile creation canceled
        """
        if self.storage.hasProfile(profile):
            info(_('The profile name already exists'))
            return defer.fail(Failure(exceptions.ConflictError))
        if not self.host.trigger.point("ProfileCreation", profile):
            return defer.fail(Failure(exceptions.CancelError))
        return self.storage.createProfile(profile)

    def deleteProfile(self, profile):
        """Delete an existing profile
        @param profile: name of the profile"""
        #TODO: async equivalent, like for createProfile
        if not self.storage.hasProfile(profile):
            error(_('Trying to delete an unknown profile'))
            return True
        if self.host.isConnected(profile):
            error(_("Trying to delete a connected profile"))
            raise exceptions.NotConnectedProfileError
        self.storage.deleteProfile(profile)
        return False

    def getProfileName(self, profile_key, return_profile_keys = False):
        """return profile according to profile_key
        @param profile_key: profile name or key which can be
                            @ALL@ for all profiles
                            @DEFAULT@ for default profile
        @param return_profile_keys: if True, return unmanaged profile keys (like "@ALL@"). This keys must be managed by the caller
        @return: requested profile name or emptry string if it doesn't exist"""
        if profile_key == '@DEFAULT@':
            default = self.host.memory.memory_data.get('Profile_default')
            if not default:
                info(_('No default profile, returning first one'))  # TODO: manage real default profile
                try:
                    default = self.host.memory.memory_data['Profile_default'] = self.storage.getProfilesList()[0]
                except IndexError:
                    info(_('No profile exist yet'))
                    return ""
            return default  # FIXME: temporary, must use real default value, and fallback to first one if it doesn't exists
        elif profile_key == '@NONE@':
            raise exceptions.ProfileNotSetError
        elif return_profile_keys and profile_key in ["@ALL@"]:
            return profile_key # this value must be managed by the caller
        if not self.storage.hasProfile(profile_key):
            info(_('Trying to access an unknown profile'))
            return "" # FIXME: raise exceptions.ProfileUnknownError here (must be well checked, this method is used in lot of places)
        return profile_key

    def __get_unique_node(self, parent, tag, name):
        """return node with given tag
        @param parent: parent of nodes to check (e.g. documentElement)
        @param tag: tag to check (e.g. "category")
        @param name: name to check (e.g. "JID")
        @return: node if it exist or None
        """
        for node in parent.childNodes:
            if node.nodeName == tag and node.getAttribute("name") == name:
                #the node already exists
                return node
        #the node is new
        return None

    def updateParams(self, xml, security_limit=NO_SECURITY_LIMIT, app=''):
        """import xml in parameters, update if the param already exists
        If security_limit is specified and greater than -1, the parameters
        that have a security level greater than security_limit are skipped.
        @param xml: parameters in xml form
        @param security_limit: -1 means no security, 0 is the maximum security then the higher the less secure
        @param app: name of the frontend registering the parameters or empty value
        """
        src_parent = minidom.parseString(xml.encode('utf-8')).documentElement

        def pre_process_app_node(src_parent, security_limit, app):
            """Parameters that are registered from a frontend must be checked"""
            to_remove = []
            for type_node in src_parent.childNodes:
                if type_node.nodeName != INDIVIDUAL:
                    to_remove.append(type_node)  # accept individual parameters only
                    continue
                for cat_node in type_node.childNodes:
                    if cat_node.nodeName != 'category':
                        to_remove.append(cat_node)
                        continue
                    to_remove_count = 0  # count the params to be removed from current category
                    for node in cat_node.childNodes:
                        if node.nodeName != "param" or not self.checkSecurityLimit(node, security_limit):
                            to_remove.append(node)
                            to_remove_count += 1
                            continue
                        node.setAttribute('app', app)
                    if len(cat_node.childNodes) == to_remove_count:  # remove empty category
                        for dummy in xrange(0, to_remove_count):
                            to_remove.pop()
                        to_remove.append(cat_node)
            for node in to_remove:
                node.parentNode.removeChild(node)

        def import_node(tgt_parent, src_parent):
            for child in src_parent.childNodes:
                if child.nodeName == '#text':
                    continue
                node = self.__get_unique_node(tgt_parent, child.nodeName, child.getAttribute("name"))
                if not node:  # The node is new
                    tgt_parent.appendChild(child)
                else:
                    if child.nodeName == "param":
                        # The child updates an existing parameter, we replace the node
                        tgt_parent.replaceChild(child, node)
                    else:
                        # the node already exists, we recurse 1 more level
                        import_node(node, child)

        if app:
            pre_process_app_node(src_parent, security_limit, app)
        import_node(self.dom.documentElement, src_parent)

    def paramsRegisterApp(self, xml, security_limit, app):
        """Register frontend's specific parameters
        If security_limit is specified and greater than -1, the parameters
        that have a security level greater than security_limit are skipped.
        @param xml: XML definition of the parameters to be added
        @param security_limit: -1 means no security, 0 is the maximum security then the higher the less secure
        @param app: name of the frontend registering the parameters
        """
        if not app:
            warning(_("Trying to register frontends parameters with no specified app: aborted"))
            return
        if not hasattr(self, "frontends_cache"):
            self.frontends_cache = []
        if app in self.frontends_cache:
            debug(_("Trying to register twice frontends parameters for %(app)s: aborted" % {"app": app}))
            return
        self.frontends_cache.append(app)
        self.updateParams(xml, security_limit, app)
        debug("Frontends parameters registered for %(app)s" % {'app': app})

    def __default_ok(self, value, name, category):
        #FIXME: will not work with individual parameters
        self.setParam(name, value, category)

    def __default_ko(self, failure, name, category):
        error(_("Can't determine default value for [%(category)s/%(name)s]: %(reason)s") % {'category': category, 'name': name, 'reason': str(failure.value)})

    def setDefault(self, name, category, callback, errback=None):
        """Set default value of parameter
        'default_cb' attibute of parameter must be set to 'yes'
        @param name: name of the parameter
        @param category: category of the parameter
        @param callback: must return a string with the value (use deferred if needed)
        @param errback: must manage the error with args failure, name, category
        """
        #TODO: send signal param update if value changed
        #TODO: manage individual paramaters
        debug ("setDefault called for %(category)s/%(name)s" % {"category": category, "name": name})
        node = self._getParamNode(name, category, '@ALL@')
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name': name, 'category': category})
            return
        if node[1].getAttribute('default_cb') == 'yes':
            # del node[1].attributes['default_cb'] # default_cb is not used anymore as a flag to know if we have to set the default value,
                                                   # and we can still use it later e.g. to call a generic setDefault method
            value = self._getParam(category, name, GENERAL)
            if value is None: # no value set by the user: we have the default value
                debug ("Default value to set, using callback")
                d = defer.maybeDeferred(callback)
                d.addCallback(self.__default_ok, name, category)
                d.addErrback(errback or self.__default_ko, name, category)

    def _getAttr(self, node, attr, value):
        """ get attribute value
        @param node: XML param node
        @param attr: name of the attribute to get (e.g.: 'value' or 'type')
        @param value: user defined value"""
        if attr == 'value':
            value_to_use = value if value is not None else node.getAttribute(attr)  # we use value (user defined) if it exist, else we use node's default value
            if node.getAttribute('type') == 'bool':
                return value_to_use.lower() not in ('false', '0', 'no')
            return value_to_use
        return node.getAttribute(attr)

    def __type_to_string(self, result):
        """ convert result to string, according to its type """
        if isinstance(result, bool):
            return "true" if result else "false"
        return result

    def getStringParamA(self, name, category, attr="value", profile_key="@NONE@"):
        """ Same as getParamA but for bridge: convert non string value to string """
        return self.__type_to_string(self.getParamA(name, category, attr, profile_key))

    def getParamA(self, name, category, attr="value", profile_key="@NONE@"):
        """Helper method to get a specific attribute
           @param name: name of the parameter
           @param category: category of the parameter
           @param attr: name of the attribute (default: "value")
           @param profile: owner of the param (@ALL@ for everyone)

           @return: attribute"""
        #FIXME: looks really dirty and buggy, need to be reviewed/refactored
        node = self._getParamNode(name, category)
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name': name, 'category': category})
            raise exceptions.NotFound

        if node[0] == GENERAL:
            value = self._getParam(category, name, GENERAL)
            return self._getAttr(node[1], attr, value)

        assert node[0] == INDIVIDUAL

        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Requesting a param for an non-existant profile'))
            raise exceptions.ProfileUnknownError

        if profile not in self.params:
            error(_('Requesting synchronous param for not connected profile'))
            raise exceptions.NotConnectedProfileError(profile)

        if attr == "value":
            value = self._getParam(category, name, profile=profile)
            return self._getAttr(node[1], attr, value)

    def asyncGetStringParamA(self, name, category, attr="value", security_limit=NO_SECURITY_LIMIT, profile_key="@NONE@"):
        d = self.asyncGetParamA(name, category, attr, security_limit, profile_key)
        d.addCallback(self.__type_to_string)
        return d

    def asyncGetParamA(self, name, category, attr="value", security_limit=NO_SECURITY_LIMIT, profile_key="@NONE@"):
        """Helper method to get a specific attribute
           @param name: name of the parameter
           @param category: category of the parameter
           @param attr: name of the attribute (default: "value")
           @param profile: owner of the param (@ALL@ for everyone)"""
        node = self._getParamNode(name, category)
        if not node:
            error(_("Requested param [%(name)s] in category [%(category)s] doesn't exist !") % {'name': name, 'category': category})
            return None

        if not self.checkSecurityLimit(node[1], security_limit):
            warning(_("Trying to get parameter '%(param)s' in category '%(cat)s' without authorization!!!"
                      % {'param': name, 'cat': category}))
            return None

        if node[0] == GENERAL:
            value = self._getParam(category, name, GENERAL)
            return defer.succeed(self._getAttr(node[1], attr, value))

        assert node[0] == INDIVIDUAL

        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Requesting a param for a non-existant profile'))
            return defer.fail()

        if attr != "value":
            return defer.succeed(node[1].getAttribute(attr))
        try:
            value = self._getParam(category, name, profile=profile)
            return defer.succeed(self._getAttr(node[1], attr, value))
        except exceptions.ProfileNotInCacheError:
            #We have to ask data to the storage manager
            d = self.storage.getIndParam(category, name, profile)
            return d.addCallback(lambda value: self._getAttr(node[1], attr, value))

    def _getParam(self, category, name, type_=INDIVIDUAL, cache=None, profile="@NONE@"):
        """Return the param, or None if it doesn't exist
        @param category: param category
        @param name: param name
        @param type_: GENERAL or INDIVIDUAL
        @param cache: temporary cache, to use when profile is not logged
        @param profile: the profile name (not profile key, i.e. name and not something like @DEFAULT@)
        @return: param value or None if it doesn't exist
        """
        if type_ == GENERAL:
            if (category, name) in self.params_gen:
                return self.params_gen[(category, name)]
            return None  # This general param has the default value
        assert (type_ == INDIVIDUAL)
        if profile == "@NONE@":
            raise exceptions.ProfileNotSetError
        if profile in self.params:
            cache = self.params[profile]  # if profile is in main cache, we use it,
                                          # ignoring the temporary cache
        elif cache is None:  # else we use the temporary cache if it exists, or raise an exception
            raise exceptions.ProfileNotInCacheError
        if (category, name) not in cache:
            return None
        return cache[(category, name)]

    def __constructProfileXml(self, security_limit, app, profile):
        """Construct xml for asked profile, filling values when needed
        /!\ as noticed in doc, don't forget to unlink the minidom.Document
        @param security_limit: NO_SECURITY_LIMIT (-1) to return all the params.
        Otherwise sole the params which have a security level defined *and*
        lower or equal to the specified value are returned.
        @param app: name of the frontend requesting the parameters, or '' to get all parameters
        @param profile: profile name (not key !)
        @return: a deferred that fire a minidom.Document of the profile xml (cf warning above)
        """

        def checkNode(node):
            """Check the node against security_limit and app"""
            return self.checkSecurityLimit(node, security_limit) and self.checkApp(node, app)

        def constructProfile(ignore, profile_cache):
            # init the result document
            prof_xml = minidom.parseString('<params/>')
            cache = {}

            for type_node in self.dom.documentElement.childNodes:
                if type_node.nodeName != GENERAL and type_node.nodeName != INDIVIDUAL:
                    continue
                # we use all params, general and individual
                for cat_node in type_node.childNodes:
                    if cat_node.nodeName != 'category':
                        continue
                    category = cat_node.getAttribute('name')
                    dest_params = {}  # result (merged) params for category
                    if category not in cache:
                        # we make a copy for the new xml
                        cache[category] = dest_cat = cat_node.cloneNode(True)
                        for node in dest_cat.childNodes:
                            if node.nodeName != "param":
                                continue
                            if not checkNode(node):
                                dest_cat.removeChild(node)
                                continue
                            dest_params[node.getAttribute('name')] = node
                        new_node = True
                    else:
                        # It's not a new node, we use the previously cloned one
                        dest_cat = cache[category]
                        new_node = False
                    params = cat_node.getElementsByTagName("param")

                    for param_node in params:
                        # we have to merge new params (we are parsing individual parameters, we have to add them
                        # to the previously parsed general ones)
                        name = param_node.getAttribute('name')
                        if not checkNode(param_node):
                            continue
                        if name not in dest_params:
                            # this is reached when a previous category exists
                            dest_params[name] = param_node.cloneNode(True)
                            dest_cat.appendChild(dest_params[name])

                        profile_value = self._getParam(category,
                                                        name, type_node.nodeName,
                                                        cache=profile_cache, profile=profile)
                        if profile_value is not None:
                            # there is a value for this profile, we must change the default
                            dest_params[name].setAttribute('value', profile_value)
                    if new_node:
                        prof_xml.documentElement.appendChild(dest_cat)

            to_remove = []
            for cat_node in prof_xml.documentElement.childNodes:
                # we remove empty categories
                if cat_node.getElementsByTagName("param").length == 0:
                    to_remove.append(cat_node)
            for node in to_remove:
                prof_xml.documentElement.removeChild(node)
            return prof_xml

        if profile in self.params:
            d = defer.succeed(None)
            profile_cache = self.params[profile]
        else:
            #profile is not in cache, we load values in a short time cache
            profile_cache = {}
            d = self.loadIndParams(profile, profile_cache)

        return d.addCallback(constructProfile, profile_cache)

    def getParamsUI(self, security_limit, app, profile_key):
        """
        @param security_limit: NO_SECURITY_LIMIT (-1) to return all the params.
        Otherwise sole the params which have a security level defined *and*
        lower or equal to the specified value are returned.
        @param app: name of the frontend requesting the parameters, or '' to get all parameters
        @param profile_key: Profile key which can be either a magic (eg: @DEFAULT@) or the name of an existing profile.
        @return: a SàT XMLUI for parameters
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return ""
        d = self.getParams(security_limit, app, profile)
        return d.addCallback(lambda param_xml: paramsXML2XMLUI(param_xml))

    def getParams(self, security_limit, app, profile_key):
        """Construct xml for asked profile, take params xml as skeleton
        @param security_limit: NO_SECURITY_LIMIT (-1) to return all the params.
        Otherwise sole the params which have a security level defined *and*
        lower or equal to the specified value are returned.
        @param app: name of the frontend requesting the parameters, or '' to get all parameters
        @param profile_key: Profile key which can be either a magic (eg: @DEFAULT@) or the name of an existing profile.
        @return: XML of parameters
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return defer.succeed("")

        def returnXML(prof_xml):
            return_xml = prof_xml.toxml()
            prof_xml.unlink()
            return '\n'.join((line for line in return_xml.split('\n') if line))

        return self.__constructProfileXml(security_limit, app, profile).addCallback(returnXML)

    def getParamsForCategory(self, category, security_limit, app, profile_key):
        """
        @param category: the desired category
        @param security_limit: NO_SECURITY_LIMIT (-1) to return all the params.
        Otherwise sole the params which have a security level defined *and*
        lower or equal to the specified value are returned.
        @param app: name of the frontend requesting the parameters, or '' to get all parameters
        @param profile_key: Profile key which can be either a magic (eg: @DEFAULT@) or the name of an existing profile.
        @return: node's xml for selected category
        """
        #TODO: manage category of general type (without existant profile)
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_("Asking params for inexistant profile"))
            return ""

        def returnCategoryXml(prof_xml):
            for node in prof_xml.getElementsByTagName("category"):
                if node.nodeName == "category" and node.getAttribute("name") == category:
                    result = node.toxml()
                    prof_xml.unlink()
                    return result

            prof_xml.unlink()
            return "<category />"

        d = self.__constructProfileXml(security_limit, app, profile)
        return d.addCallback(returnCategoryXml)

    def _getParamNode(self, name, category, type_="@ALL@"):  # FIXME: is type_ useful ?
        """Return a node from the param_xml
        @param name: name of the node
        @param category: category of the node
        @type_: keyword for search:
                                    @ALL@ search everywhere
                                    @GENERAL@ only search in general type
                                    @INDIVIDUAL@ only search in individual type
        @return: a tuple with the node type and the the node, or None if not found"""

        for type_node in self.dom.documentElement.childNodes:
            if (((type_ == "@ALL@" or type_ == "@GENERAL@") and type_node.nodeName == GENERAL)
                    or ((type_ == "@ALL@" or type_ == "@INDIVIDUAL@") and type_node.nodeName == INDIVIDUAL)):
                for node in type_node.getElementsByTagName('category'):
                    if node.getAttribute("name") == category:
                        params = node.getElementsByTagName("param")
                        for param in params:
                            if param.getAttribute("name") == name:
                                return (type_node.nodeName, param)
        return None

    def getParamsCategories(self):
        """return the categories availables"""
        categories = []
        for cat in self.dom.getElementsByTagName("category"):
            name = cat.getAttribute("name")
            if name not in categories:
                categories.append(cat.getAttribute("name"))
        return categories

    def setParam(self, name, value, category, security_limit=NO_SECURITY_LIMIT, profile_key='@NONE@'):
        """Set a parameter, return None if the parameter is not in param xml"""
        #TODO: use different behaviour depending of the data type (e.g. password encrypted)
        if profile_key != "@NONE@":
            profile = self.getProfileName(profile_key)
            if not profile:
                error(_('Trying to set parameter for an unknown profile'))
                return  # TODO: throw an error

        node = self._getParamNode(name, category, '@ALL@')
        if not node:
            error(_('Requesting an unknown parameter (%(category)s/%(name)s)')
                  % {'category': category, 'name': name})
            return

        if not self.checkSecurityLimit(node[1], security_limit):
            warning(_("Trying to set parameter '%(param)s' in category '%(cat)s' without authorization!!!"
                          % {'param': name, 'cat': category}))
            return

        if node[0] == GENERAL:
            self.params_gen[(category, name)] = value
            self.storage.setGenParam(category, name, value)
            for profile in self.storage.getProfilesList():
                if self.host.isConnected(profile):
                    self.host.bridge.paramUpdate(name, value, category, profile)
                    self.host.trigger.point("paramUpdateTrigger", name, value, category, node[0], profile)
            return

        assert (node[0] == INDIVIDUAL)
        assert (profile_key != "@NONE@")

        type_ = node[1].getAttribute("type")
        if type_ == "button":
            print "clique", node.toxml()
        else:
            if self.host.isConnected(profile):  # key can not exists if profile is not connected
                self.params[profile][(category, name)] = value
            self.host.bridge.paramUpdate(name, value, category, profile)
            self.host.trigger.point("paramUpdateTrigger", name, value, category, node[0], profile)
            self.storage.setIndParam(category, name, value, profile)

    def checkSecurityLimit(self, node, security_limit):
        """Check the given node against the given security limit.
        The value NO_SECURITY_LIMIT (-1) means that everything is allowed.
        @return: True if this node can be accessed with the given security limit.
        """
        if security_limit < 0:
            return True
        if node.hasAttribute("security"):
            if int(node.getAttribute("security")) <= security_limit:
                return True
        return False

    def checkApp(self, node, app):
        """Check the given node against the given app.
        @param node: parameter node
        @param app: name of the frontend requesting the parameters, or '' to get all parameters
        @return: True if this node concerns the given app.
        """
        if not app or not node.hasAttribute("app"):
            return True
        return node.getAttribute("app") == app


class Memory(object):
    """This class manage all persistent informations"""

    def __init__(self, host):
        info(_("Memory manager init"))
        self.initialized = defer.Deferred()
        self.host = host
        self.entitiesCache = {}  # XXX: keep presence/last resource/other data in cache
                                 #     /!\ an entity is not necessarily in roster
        self.subscriptions = {}
        self.server_features = {}  # used to store discovery's informations
        self.server_identities = {}
        self.config = self.parseMainConf()
        host.setConst('savefile_database', SAVEFILE_DATABASE)
        database_file = os.path.expanduser(self.getConfig('', 'local_dir') +
                                           self.host.getConst('savefile_database'))
        self.storage = SqliteStorage(database_file, host.__version__)
        PersistentDict.storage = self.storage
        self.params = Params(host, self.storage)
        info(_("Loading default params template"))
        self.params.load_default_params()
        d = self.storage.initialized.addCallback(lambda ignore: self.load())
        self.memory_data = PersistentDict("memory")
        d.addCallback(lambda ignore: self.memory_data.load())
        d.chainDeferred(self.initialized)

    def parseMainConf(self):
        """look for main .ini configuration file, and parse it"""
        _config = SafeConfigParser(defaults=default_config)
        try:
            _config.read(map(os.path.expanduser, ['/etc/sat.conf', '~/sat.conf', '~/.sat.conf', 'sat.conf', '.sat.conf']))
        except:
            error(_("Can't read main config !"))

        return _config

    def getConfig(self, section, name):
        """Get the main configuration option
        @param section: section of the config file (None or '' for DEFAULT)
        @param name: name of the option
        """
        if not section:
            section = 'DEFAULT'
        try:
            value = self.config.get(section, name)
        except (NoOptionError, NoSectionError):
            value = ''

        if name.endswith('_path') or name.endswith('_dir'):
            value = os.path.expanduser(value)
        # thx to Brian (http://stackoverflow.com/questions/186857/splitting-a-semicolon-separated-string-to-a-dictionary-in-python/186873#186873)
        elif name.endswith('_list'):
            value = csv.reader([value], delimiter=',', quotechar='"').next()
        elif name.endswith('_dict'):
            value = dict(csv.reader([item], delimiter=':', quotechar='"').next()
                         for item in csv.reader([value], delimiter=',', quotechar='"').next())
        return value

    def load_xml(self, filename):
        """Load parameters template from xml file"""
        if filename is None:
            return False
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            try:
                self.params.load_xml(filename)
                debug(_("Parameters loaded from file: %s") % filename)
                return True
            except Exception as e:
                error(_("Can't load parameters from file: %s") % e)
        return False

    def load(self):
        """Load parameters and all memory things from db"""
        #parameters data
        return self.params.loadGenParams()

    def loadIndividualParams(self, profile):
        """Load individual parameters for a profile
        @param profile: %(doc_profile)s"""
        return self.params.loadIndParams(profile)

    def startProfileSession(self, profile):
        """"Iniatialise session for a profile
        @param profile: %(doc_profile)s"""
        info(_("[%s] Profile session started" % profile))
        self.entitiesCache[profile] = {}

    def purgeProfileSession(self, profile):
        """Delete cache of data of profile
        @param profile: %(doc_profile)s"""
        info(_("[%s] Profile session purge" % profile))
        self.params.purgeProfile(profile)
        try:
            del self.entitiesCache[profile]
        except KeyError:
            error(_("Trying to purge roster status cache for a profile not in memory: [%s]") % profile)

    def save_xml(self, filename=None):
        """Save parameters template to xml file"""
        if filename is None:
            return False
        #TODO: need to encrypt files (at least passwords !) and set permissions
        filename = os.path.expanduser(filename)
        try:
            self.params.save_xml(filename)
            debug(_("Parameters saved to file: %s") % filename)
            return True
        except Exception as e:
            error(_("Can't save parameters to file: %s") % e)
        return False

    def getProfilesList(self):
        return self.storage.getProfilesList()

    def getProfileName(self, profile_key, return_profile_keys = False):
        """Return name of profile from keyword
        @param profile_key: can be the profile name or a keywork (like @DEFAULT@)
        @return: profile name or None if it doesn't exist"""
        return self.params.getProfileName(profile_key, return_profile_keys)

    def createProfile(self, name):
        """Create a new profile
        @param name: Profile name
        """
        return self.params.createProfile(name)

    def asyncCreateProfile(self, name):
        """Create a new profile
        @param name: Profile name
        """
        return self.params.asyncCreateProfile(name)

    def deleteProfile(self, name):
        """Delete an existing profile
        @param name: Name of the profile"""
        return self.params.deleteProfile(name)

    def addToHistory(self, from_jid, to_jid, message, type_='chat', extra=None, timestamp=None, profile="@NONE@"):
        assert profile != "@NONE@"
        if extra is None:
            extra = {}
        return self.storage.addToHistory(from_jid, to_jid, message, type_, extra, timestamp, profile)

    def getHistory(self, from_jid, to_jid, limit=0, between=True, profile="@NONE@"):
        assert profile != "@NONE@"
        return self.storage.getHistory(jid.JID(from_jid), jid.JID(to_jid), limit, between, profile)

    def addServerFeature(self, feature, jid_, profile):
        """Add a feature discovered from server
        @param feature: string of the feature
        @param jid_: the jid of the target server
        @param profile: which profile asked this server?"""
        if profile not in self.server_features:
            self.server_features[profile] = {}
        features = self.server_features[profile].setdefault(jid_, [])
        features.append(feature)

    def addServerIdentity(self, category, type_, entity, jid_, profile):
        """Add an identity discovered from server
        @param feature: string of the feature
        @param jid_: the jid of the target server
        @param profile: which profile asked this server?"""
        if not profile in self.server_identities:
            self.server_identities[profile] = {}
        identities = self.server_identities[profile].setdefault(jid_, {})
        if (category, type_) not in identities:
            identities[(category, type_)] = set()
        identities[(category, type_)].add(entity)

    def getServerServiceEntities(self, category, type_, jid_=None, profile=None):
        """Return all available entities of a server for the service (category, type_)
        @param category: identity's category
        @param type_: identitiy's type
        @param jid_: the jid of the target server (None for profile's server)
        @param profile: which profile is asking this server?
        @return: a set of entities or None if no cached data were found
        """
        if jid_ is None:
            jid_ = self.host.getClientHostJid(profile)
        if profile in self.server_identities and jid_ in self.server_identities[profile]:
            return self.server_identities[profile][jid_].get((category, type_), set())
        else:
            return None

    def getServerServiceEntity(self, category, type_, jid_=None, profile=None):
        """Helper method to get first available entity of a server for the service (category, type_)
        @param category: identity's category
        @param type_: identitiy's type
        @param jid_: the jid of the target server (None for profile's server)
        @param profile: which profile is asking this server?
        @return: the first found entity or None if no cached data were found
        """
        entities = self.getServerServiceEntities(category, type_, jid_, profile)
        if entities is None:
            warning(_("Entities (%(category)s/%(type)s) of %(server)s not available, maybe they haven't been asked yet?")
                    % {"category": category, "type": type_, "server": jid_})
            return None
        else:
            return list(entities)[0] if entities else None

    def getAllServerIdentities(self, jid_, profile):
        """Helper method to get all identities of a server
        @param jid_: the jid of the target server (None for profile's server)
        @param profile: which profile is asking this server?
        @return: a set of entities or None if no cached data were found
        """
        if jid_ is None:
            jid_ = self.host.getClientHostJid(profile)
        if jid_ not in self.server_identities[profile]:
            return None
        entities = set()
        for set_ in self.server_identities[profile][jid_].values():
            entities.update(set_)
        return entities

    def hasServerFeature(self, feature, jid_=None, profile_key="@NONE@"):
        """Tell if the specified server has the required feature
        @param feature: requested feature
        @param jid_: the jid of the target server (None for profile's server)
        @param profile: which profile is asking this server?
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Trying find server feature for a non-existant profile'))
            return None
        assert profile in self.server_features
        if jid_ is None:
            jid_ = self.host.getClientHostJid(profile)
        if jid_ in self.server_features[profile]:
            return feature in self.server_features[profile][jid_]
        else:
            warning(_("Features of %s not available, maybe they haven't been asked yet?") % jid_)
            return None

    def getLastResource(self, contact, profile_key):
        """Return the last resource used by a contact
        @param contact: contact jid (unicode)
        @param profile_key: %(doc_profile_key)s"""
        profile = self.getProfileName(profile_key)
        if not profile or not self.host.isConnected(profile):
            error(_('Asking contacts for a non-existant or not connected profile'))
            return ""
        entity = jid.JID(contact).userhost()
        if not entity in self.entitiesCache[profile]:
            info(_("Entity not in cache"))
            return ""
        try:
            return self.entitiesCache[profile][entity]["last_resource"]
        except KeyError:
            return ""

    def getPresenceStatus(self, profile_key):
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Asking contacts for a non-existant profile'))
            return {}
        entities_presence = {}
        for entity in self.entitiesCache[profile]:
            if "presence" in self.entitiesCache[profile][entity]:
                entities_presence[entity] = self.entitiesCache[profile][entity]["presence"]

        debug("Memory getPresenceStatus (%s)", entities_presence)
        return entities_presence

    def setPresenceStatus(self, entity_jid, show, priority, statuses, profile_key):
        """Change the presence status of an entity"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Trying to add presence status to a non-existant profile'))
            return
        entity_data = self.entitiesCache[profile].setdefault(entity_jid.userhost(), {})
        resource = jid.parse(entity_jid.full())[2] or ''
        if resource:
            entity_data["last_resource"] = resource
        if not "last_resource" in entity_data:
            entity_data["last_resource"] = ''

        entity_data.setdefault("presence", {})[resource] = (show, priority, statuses)

    def updateEntityData(self, entity_jid, key, value, profile_key):
        """Set a misc data for an entity
        @param entity_jid: JID of the entity, or '@ALL@' to update all entities)
        @param key: key to set (eg: "type")
        @param value: value for this key (eg: "chatroom"), or '@NONE@' to delete
        @param profile_key: %(doc_profile_key)s
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileUnknownError(_('Trying to get entity data for a non-existant profile'))
        if not profile in self.entitiesCache:
            raise exceptions.ProfileNotInCacheError
        if entity_jid == "@ALL@":
            entities_map = self.entitiesCache[profile]
        else:
            entity = entity_jid.userhost()
            self.entitiesCache[profile].setdefault(entity, {})
            entities_map = {entity: self.entitiesCache[profile][entity]}
        for entity in entities_map:
            entity_map = entities_map[entity]
            if value == "@NONE@" and key in entity_map:
                del entity_map[key]
            else:
                entity_map[key] = value
            if isinstance(value, basestring):
                self.host.bridge.entityDataUpdated(entity, key, value, profile)

    def getEntityData(self, entity_jid, keys_list, profile_key):
        """Get a list of cached values for entity
        @param entity_jid: JID of the entity
        @param keys_list: list of keys to get, empty list for everything
        @param profile_key: %(doc_profile_key)s
        @return: dict withs values for each key in keys_list.
                 if there is no value of a given key, resulting dict will
                 have nothing with that key nether
        @raise: exceptions.UnknownEntityError if entity is not in cache
                exceptions.ProfileNotInCacheError if profile is not in cache
        """
        profile = self.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileUnknownError(_('Trying to get entity data for a non-existant profile'))
        if not profile in self.entitiesCache:
            raise exceptions.ProfileNotInCacheError
        if not entity_jid.userhost() in self.entitiesCache[profile]:
            raise exceptions.UnknownEntityError(entity_jid.userhost())
        entity_data = self.entitiesCache[profile][entity_jid.userhost()]
        if not keys_list:
            return entity_data
        ret = {}
        for key in keys_list:
            if key in entity_data:
                ret[key] = entity_data[key]
        return ret

    def delEntityCache(self, entity_jid, profile_key):
        """Remove cached data for entity
        @param entity_jid: JID of the entity
        """
        profile = self.getProfileName(profile_key)
        try:
            del self.entitiesCache[profile][entity_jid.userhost()]
        except KeyError:
            pass

    def addWaitingSub(self, type_, entity_jid, profile_key):
        """Called when a subcription request is received"""
        profile = self.getProfileName(profile_key)
        assert profile
        if profile not in self.subscriptions:
            self.subscriptions[profile] = {}
        self.subscriptions[profile][entity_jid] = type_

    def delWaitingSub(self, entity_jid, profile_key):
        """Called when a subcription request is finished"""
        profile = self.getProfileName(profile_key)
        assert profile
        if profile in self.subscriptions and entity_jid in self.subscriptions[profile]:
            del self.subscriptions[profile][entity_jid]

    def getWaitingSub(self, profile_key):
        """Called to get a list of currently waiting subscription requests"""
        profile = self.getProfileName(profile_key)
        if not profile:
            error(_('Asking waiting subscriptions for a non-existant profile'))
            return {}
        if profile not in self.subscriptions:
            return {}

        return self.subscriptions[profile]

    def getStringParamA(self, name, category, attr="value", profile_key='@NONE@'):
        return self.params.getStringParamA(name, category, attr, profile_key)

    def getParamA(self, name, category, attr="value", profile_key='@NONE@'):
        return self.params.getParamA(name, category, attr, profile_key)

    def asyncGetParamA(self, name, category, attr="value", security_limit=NO_SECURITY_LIMIT, profile_key='@NONE@'):
        return self.params.asyncGetParamA(name, category, attr, security_limit, profile_key)

    def asyncGetStringParamA(self, name, category, attr="value", security_limit=NO_SECURITY_LIMIT, profile_key='@NONE@'):
        return self.params.asyncGetStringParamA(name, category, attr, security_limit, profile_key)

    def getParamsUI(self, security_limit=NO_SECURITY_LIMIT, app='', profile_key='@NONE@'):
        return self.params.getParamsUI(security_limit, app, profile_key)

    def getParams(self, security_limit=NO_SECURITY_LIMIT, app='', profile_key='@NONE@'):
        return self.params.getParams(security_limit, app, profile_key)

    def getParamsForCategory(self, category, security_limit=NO_SECURITY_LIMIT, app='', profile_key='@NONE@'):
        return self.params.getParamsForCategory(category, security_limit, app, profile_key)

    def getParamsCategories(self):
        return self.params.getParamsCategories()

    def setParam(self, name, value, category, security_limit=NO_SECURITY_LIMIT, profile_key='@NONE@'):
        return self.params.setParam(name, value, category, security_limit, profile_key)

    def updateParams(self, xml):
        return self.params.updateParams(xml)

    def paramsRegisterApp(self, xml, security_limit=NO_SECURITY_LIMIT, app=''):
        return self.params.paramsRegisterApp(xml, security_limit, app)

    def setDefault(self, name, category, callback, errback=None):
        return self.params.setDefault(name, category, callback, errback)
