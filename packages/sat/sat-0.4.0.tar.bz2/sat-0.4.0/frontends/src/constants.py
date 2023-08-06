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


from sat.core.i18n import _, D_

try:
    from collections import OrderedDict  # only available from python 2.7
except ImportError:
    try:
        from ordereddict import OrderedDict
    except ImportError:
        pass  # libervia can not import external libraries


def getPresence():
    """We cannot do it directly in the Const class, if it is not encapsulated
    in a method we get a JS runtime SyntaxError: "missing ) in parenthetical".
    # TODO: merge this definition with those in primitivus.constants and wix.constants
    """
    try:
        presence = OrderedDict([("", _("Online")),
                                ("chat", _("Free for chat")),
                                ("away", _("Away from keyboard")),
                                ("dnd", _("Do not disturb")),
                                ("xa", _("Away"))])
    except TypeError:
        presence = {"": _("Online"),
                    "chat": _("Free for chat"),
                    "away": _("Away from keyboard"),
                    "dnd": _("Do not disturb"),
                    "xa": _("Away")
                    }
    return presence


class Const(object):
    PRESENCE = getPresence()

    MENU_NORMAL = "NORMAL"

    # from plugin_misc_text_syntaxes
    SYNTAX_XHTML = "XHTML"
    SYNTAX_CURRENT = "@CURRENT@"

    NO_SECURITY_LIMIT = -1

    #XMLUI
    SAT_FORM_PREFIX = "SAT_FORM_"
    SAT_PARAM_SEPARATOR = "_XMLUI_PARAM_" # used to have unique elements names
