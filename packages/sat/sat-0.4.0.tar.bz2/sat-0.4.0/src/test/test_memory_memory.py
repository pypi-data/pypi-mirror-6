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

from sat.core.i18n import _
from sat.test import helpers
from twisted.trial import unittest
import traceback
import logging
from constants import Const
from xml.dom import minidom


class MemoryTest(unittest.TestCase):

    def setUp(self):
        self.host = helpers.FakeSAT()

    def _getParamXML(self, param="1", security_level=None):
        def getParam(name):
            return """
            <param name="%(param_name)s" label="%(param_label)s" value="true" type="bool" %(security)s/>
            """ % {'param_name': name,
                            'param_label': _(name),
                            'security': '' if security_level is None else ('security="%d"' % security_level)
                            }
        if param == "1":
            params = getParam(Const.ENABLE_UNIBOX_PARAM)
        elif param == "2":
            params = getParam(Const.PARAM_IN_QUOTES)
        else:
            params = getParam(Const.ENABLE_UNIBOX_PARAM) + getParam(Const.PARAM_IN_QUOTES)
        return """
        <params>
        <individual>
        <category name="%(category_name)s" label="%(category_label)s">
            %(params)s
         </category>
        </individual>
        </params>
        """ % {
            'category_name': Const.COMPOSITION_KEY,
            'category_label': _(Const.COMPOSITION_KEY),
            'params': params
        }

    def _paramExists(self, param="1", src=None):
        """@return: True is the param (category, name) exists"""
        if param == "1":
            name = Const.ENABLE_UNIBOX_PARAM
        else:
            name = Const.PARAM_IN_QUOTES
        category = Const.COMPOSITION_KEY
        if src is None:
            src = self.host.memory.params.dom.documentElement
        for type_node in src.childNodes:
            # when src comes self.host.memory.params.dom, we have here
            # some "individual" or "general" elements, when it comes
            # from Memory.getParams we have here a "params" elements
            if type_node.nodeName not in ("individual", "general", "params"):
                continue
            for cat_node in type_node.childNodes:
                if cat_node.nodeName != "category" or cat_node.getAttribute("name") != category:
                    continue
                for param in cat_node.childNodes:
                    if param.nodeName == "param" and param.getAttribute("name") == name:
                        return True
        return False

    def assertParam_generic(self, param="1", src=None, exists=True, deferred=False):
        msg = "Expected parameter not found!\n" if exists else "Unexpected parameter found!\n"
        if deferred == False:
            # in this stack we can see the line where the error came from,
            # if limit=5, 6 is not enough you can increase the value
            msg += "\n".join(traceback.format_stack(limit=5 if exists else 6))
        assertion = self._paramExists(param, src)
        getattr(self, "assert%s" % exists)(assertion, msg)

    def assertParamExists(self, param="1", src=None):
        self.assertParam_generic(param, src, True)

    def assertParamNotExists(self, param="1", src=None):
        self.assertParam_generic(param, src, False)

    def assertParamExists_async(self, src, param="1"):
        """@param src: a deferred result from Memory.getParams"""
        self.assertParam_generic(param, minidom.parseString(src.encode("utf-8")), True, True)

    def assertParamNotExists_async(self, src, param="1"):
        """@param src: a deferred result from Memory.getParams"""
        self.assertParam_generic(param, minidom.parseString(src.encode("utf-8")), False, True)

    def _getParams(self, security_limit, app='', profile_key='@NONE@'):
        if profile_key == '@NONE@':
            profile_key = '@DEFAULT@'
        return self.host.memory.getParams(security_limit, app, profile_key)

    def test_updateParams(self):
        self.host.memory.init()
        # check if the update works
        self.host.memory.updateParams(self._getParamXML())
        self.assertParamExists()
        previous = self.host.memory.params.dom.cloneNode(True)
        # now check if it is really updated and not duplicated
        self.host.memory.updateParams(self._getParamXML())
        self.assertEqual(previous.toxml().encode("utf-8"), self.host.memory.params.dom.toxml().encode("utf-8"))

        self.host.memory.init()
        # check successive updates (without intersection)
        self.host.memory.updateParams(self._getParamXML('1'))
        self.assertParamExists("1")
        self.assertParamNotExists("2")
        self.host.memory.updateParams(self._getParamXML('2'))
        self.assertParamExists("1")
        self.assertParamExists("2")

        previous = self.host.memory.params.dom.cloneNode(True)  # save for later

        self.host.memory.init()
        # check successive updates (with intersection)
        self.host.memory.updateParams(self._getParamXML('1'))
        self.assertParamExists("1")
        self.assertParamNotExists("2")
        self.host.memory.updateParams(self._getParamXML('both'))
        self.assertParamExists("1")
        self.assertParamExists("2")

        # successive updates with or without intersection should have the same result
        self.assertEqual(previous.toxml().encode("utf-8"), self.host.memory.params.dom.toxml().encode("utf-8"))

    def test_getParams(self):
        # tests with no security level on the parameter (most secure)
        params = self._getParamXML()
        self.host.memory.init()
        self.host.memory.updateParams(params)
        self._getParams(Const.NO_SECURITY_LIMIT).addCallback(self.assertParamExists_async)
        self._getParams(0).addCallback(self.assertParamNotExists_async)
        self._getParams(1).addCallback(self.assertParamNotExists_async)
        # tests with security level 0 on the parameter (not secure)
        params = self._getParamXML(security_level=0)
        self.host.memory.init()
        self.host.memory.updateParams(params)
        self._getParams(Const.NO_SECURITY_LIMIT).addCallback(self.assertParamExists_async)
        self._getParams(0).addCallback(self.assertParamExists_async)
        self._getParams(1).addCallback(self.assertParamExists_async)
        # tests with security level 1 on the parameter (more secure)
        params = self._getParamXML(security_level=1)
        self.host.memory.init()
        self.host.memory.updateParams(params)
        self._getParams(Const.NO_SECURITY_LIMIT).addCallback(self.assertParamExists_async)
        self._getParams(0).addCallback(self.assertParamNotExists_async)
        self._getParams(1).addCallback(self.assertParamExists_async)

    def test_paramsRegisterApp(self):

        def register(*args):
            logger = logging.getLogger()
            level = logger.getEffectiveLevel()
            logger.setLevel(logging.INFO)
            self.host.memory.paramsRegisterApp(*args)
            logger.setLevel(level)

        # tests with no security level on the parameter (most secure)
        params = self._getParamXML()
        self.host.memory.init()
        register(params, Const.NO_SECURITY_LIMIT, Const.APP_NAME)
        self.assertParamExists()
        self.host.memory.init()
        register(params, 0, Const.APP_NAME)
        self.assertParamNotExists()
        self.host.memory.init()
        register(params, 1, Const.APP_NAME)
        self.assertParamNotExists()

        # tests with security level 0 on the parameter (not secure)
        params = self._getParamXML(security_level=0)
        self.host.memory.init()
        register(params, Const.NO_SECURITY_LIMIT, Const.APP_NAME)
        self.assertParamExists()
        self.host.memory.init()
        register(params, 0, Const.APP_NAME)
        self.assertParamExists()
        self.host.memory.init()
        register(params, 1, Const.APP_NAME)
        self.assertParamExists()

        # tests with security level 1 on the parameter (more secure)
        params = self._getParamXML(security_level=1)
        self.host.memory.init()
        register(params, Const.NO_SECURITY_LIMIT, Const.APP_NAME)
        self.assertParamExists()
        self.host.memory.init()
        register(params, 0, Const.APP_NAME)
        self.assertParamNotExists()
        self.host.memory.init()
        register(params, 1, Const.APP_NAME)
        self.assertParamExists()

    def test_paramsRegisterApp_getParams(self):
        # test retrieving the parameter for a specific frontend
        self.host.memory.init()
        params = self._getParamXML(security_level=1)
        self.host.memory.paramsRegisterApp(params, 1, Const.APP_NAME)
        self._getParams(1, '').addCallback(self.assertParamExists_async)
        self._getParams(1, Const.APP_NAME).addCallback(self.assertParamExists_async)
        self._getParams(1, 'another_dummy_frontend').addCallback(self.assertParamNotExists_async)
