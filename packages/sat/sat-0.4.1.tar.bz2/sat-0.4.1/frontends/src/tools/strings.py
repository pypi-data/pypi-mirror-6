#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT helpers methods for plugins
# Copyright (C) 2013, 2014 Adrien Cossa (souliane@mailoo.org)

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

import re


def getURLParams(url):
    """This comes from pyjamas.Location.makeUrlDict with a small change
    to also parse full URLs, and parameters with no value specified
    (in that case the default value "" is used).
    @param url: any URL with or without parameters
    @return: a dictionary of the parameters, if any was given, or {}
    """
    dict_ = {}
    if "/" in url:
        # keep the part after the last "/"
        url = url[url.rindex("/") + 1:]
    if url.startswith("?"):
        # remove the first "?"
        url = url[1:]
    pairs = url.split("&")
    for pair in pairs:
        if len(pair) < 3:
            continue
        kv = pair.split("=", 1)
        dict_[kv[0]] = kv[1] if len(kv) > 1 else ""
    return dict_


def addURLToText(string):
    """Check a text for what looks like an URL and make it clickable. Regexp
    from http://daringfireball.net/2010/07/improved_regex_for_matching_urls"""

    def repl(match):
        url = match.group(0)
        if not re.match(r"""[a-z]{3,}://|mailto:|xmpp:""", url):
            url = "http://" + url
        return '<a href="%s" target="_blank" class="url">%s</a>' % (url, match.group(0))
    pattern = r"""(?i)\b((?:[a-z]{3,}://|(www|ftp)\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/|mailto:|xmpp:)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))"""
    return re.sub(pattern, repl, string)


def addURLToImage(string):
    """Check a XHTML text for what looks like an imageURL and make it clickable"""
    def repl(match):
        url = match.group(1)
        return '<a href="%s" target="_blank">%s</a>' % (url, match.group(0))
    pattern = r"""<img[^>]* src="([^"]+)"[^>]*>"""
    return re.sub(pattern, repl, string)
