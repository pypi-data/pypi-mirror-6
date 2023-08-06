#!/usr/bin/python
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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
import sys
import os.path
import gettext
import sat_frontends.wix
from sat_frontends.quick_frontend import constants


_ = gettext.gettext
wix_root = os.path.dirname(sat_frontends.wix.__file__)


class Const(constants.Const):

    APP_NAME = "Wix"
    LICENCE_PATH = os.path.join(wix_root, "COPYING")
    msgOFFLINE = _("offline")
    msgONLINE = _("online")
    DEFAULT_GROUP = "Unclassed"
    PRESENCE = [("", _("Online"), None),
                ("chat", _("Free for chat"), "green"),
                ("away", _("AFK"), "brown"),
                ("dnd", _("DND"), "red"),
                ("xa", _("Away"), "red")
                ]

