#!/usr/bin/python
# -*- coding: utf-8 -*-

# SAT plugin for managing various text syntaxes
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
from logging import debug, info, error, warning

from wokkel import disco, pubsub
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from sat.core import exceptions
from lxml import html
from lxml.html import clean
from cgi import escape
import re


CATEGORY = D_("Composition")
NAME = "Syntax"
_SYNTAX_XHTML = "XHTML"
_SYNTAX_CURRENT = "@CURRENT@"

# TODO: check/adapt following list
STYLES_WHITELIST = ["azimuth", "background-color", "border-bottom-color", "border-collapse", "border-color", "border-left-color", "border-right-color", "border-top-color", "clear", "color", "cursor", "direction", "display", "elevation", "float", "font", "font-family", "font-size", "font-style", "font-variant", "font-weight", "height", "letter-spacing", "line-height", "overflow", "pause", "pause-after", "pause-before", "pitch", "pitch-range", "richness", "speak", "speak-header", "speak-numeral", "speak-punctuation", "speech-rate", "stress", "text-align", "text-decoration", "text-indent", "unicode-bidi", "vertical-align", "voice-family", "volume", "white-space", "width"] # based on feedparser list (http://pythonhosted.org/feedparser/html-sanitization.html)

SAFE_ATTRS = html.defs.safe_attrs.union(('style',))
STYLES_VALUES_REGEX = r'^(' + '|'.join(['([a-z-]+)', # alphabetical names
                                       '(#[0-9a-f]+)', # hex value
                                       '(\d+(.\d+)? *(|%|em|ex|px|in|cm|mm|pt|pc))', # values with units (or not)
                                       'rgb\( *((\d+(.\d+)?), *){2}(\d+(.\d+)?) *\)', # rgb function
                                       'rgba\( *((\d+(.\d+)?), *){3}(\d+(.\d+)?) *\)', # rgba function
                                      ]) + ') *(!important)?$' # we accept "!important" at the end
STYLES_ACCEPTED_VALUE = re.compile(STYLES_VALUES_REGEX)

PLUGIN_INFO = {
    "name": "Text syntaxes",
    "import_name": "TEXT-SYNTAXES",
    "type": "MISC",
    "protocols": [],
    "dependencies": [],
    "main": "TextSyntaxes",
    "handler": "no",
    "description": _("""Management of various text syntaxes (XHTML-IM, Markdown, etc)""")
}

class UnknownSyntax(Exception):
    pass

class TextSyntaxes(object):
    """ Text conversion class
    XHTML utf-8 is used as intermediate language for conversions
    """

    OPT_DEFAULT = "DEFAULT"
    OPT_HIDDEN = "HIDDEN"
    OPT_NO_THREAD = "NO_THREAD"
    SYNTAX_XHTML = _SYNTAX_XHTML
    SYNTAX_MARKDOWN = "markdown"
    SYNTAX_TEXT = "text"

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(name)s" label="%(label)s"
           value="%(default)s" type="list" security="0">
            %(options)s
        </param>
    </category>
    </individual>
    </params>
    """

    params_data = {
        'category_name': CATEGORY,
        'category_label': _(CATEGORY),
        'name': NAME,
        'label': _(NAME),
        'default': _SYNTAX_XHTML,
        'syntaxes': {},
        }

    def __init__(self, host):
        info(_("Text syntaxes plugin initialization"))
        self.host = host
        self.syntaxes = {}
        self.addSyntax(self.SYNTAX_XHTML, lambda xhtml: defer.succeed(xhtml), lambda xhtml: defer.succeed(xhtml),
                       TextSyntaxes.OPT_NO_THREAD)
        self.addSyntax(self.SYNTAX_TEXT, lambda text: escape(text), lambda xhtml: self._removeMarkups(xhtml), [TextSyntaxes.OPT_HIDDEN])
        try:
            import markdown, html2text

            def _html2text(html, baseurl=''):
                h = html2text.HTML2Text(baseurl=baseurl)
                h.body_width = 0  # do not truncate the lines, it breaks the long URLs
                return h.handle(html)
            self.addSyntax(self.SYNTAX_MARKDOWN, markdown.markdown, _html2text, [TextSyntaxes.OPT_DEFAULT])
        except ImportError:
            warning("markdown or html2text not found, can't use Markdown syntax")
        host.bridge.addMethod("syntaxConvert", ".plugin", in_sign='sssbs', out_sign='s',
                              async=True, method=self.convert)

    def _updateParamOptions(self):
        data_synt = TextSyntaxes.params_data['syntaxes']
        syntaxes = []

        for syntax in data_synt.keys():
            flags = data_synt[syntax]["flags"]
            if TextSyntaxes.OPT_HIDDEN not in flags:
                syntaxes.append(syntax)

        syntaxes.sort(key=unicode.lower)
        options = []

        for syntax in syntaxes:
            options.append(u'<option value="%s" />' % syntax)

        TextSyntaxes.params_data["options"] = u'\n'.join(options)
        self.host.memory.updateParams(TextSyntaxes.params % TextSyntaxes.params_data)

    def getCurrentSyntax(self, profile):
        """ Return the selected syntax for the given profile

        @param profile: %(doc_profile)s
        @return: profile selected syntax
        """
        return self.host.memory.getParamA(NAME, CATEGORY , profile_key=profile)

    def clean_xhtml(self, xhtml):
        """ Clean XHTML text by removing potentially dangerous/malicious parts
        @param xhtml: raw xhtml text to clean (or lxml's HtmlElement)
        """
        def blocking_cleaning(xhtml):
            """ Clean XHTML and style attributes """

            def clean_style(styles_raw):
                """" Remove styles not in the whitelist,
                or where the value doesn't match the regex """
                styles = styles_raw.split(";")
                cleaned_styles = []
                for style in styles:
                    try:
                        key, value = style.split(':')
                    except ValueError:
                        continue
                    key = key.lower().strip()
                    if key not in STYLES_WHITELIST:
                        continue
                    value = value.lower().strip()
                    if not STYLES_ACCEPTED_VALUE.match(value):
                        continue
                    if value == "none":
                        continue
                    cleaned_styles.append((key, value))
                return "; ".join(["%s: %s" % (key, value) for key, value in cleaned_styles])

            if isinstance(xhtml, basestring):
                xhtml_elt = html.fromstring(xhtml)
            elif isinstance(xhtml, html.HtmlElement):
                xhtml_elt = xhtml
            else:
                error("Only strings and HtmlElements can be cleaned")
                raise exceptions.DataError
            cleaner = clean.Cleaner(style=False,
                                    add_nofollow=False,
                                    safe_attrs=SAFE_ATTRS)
            xhtml_elt = cleaner.clean_html(xhtml_elt)
            for elt in xhtml_elt.xpath("//*[@style]"):
                elt.set("style", clean_style(elt.get('style')))
            return html.tostring(xhtml_elt, encoding=unicode, method='xml')

        return deferToThread(blocking_cleaning, xhtml)

    def convert(self, text, syntax_from, syntax_to=_SYNTAX_XHTML, safe=True, profile=None):
        """ Convert a text between two syntaxes
        @param text: text to convert
        @param syntax_from: source syntax (e.g. "markdown")
        @param syntax_to: dest syntax (e.g.: "XHTML")
        @param safe: clean resulting XHTML to avoid malicious code if True
        @param profile: needed only when syntax_from or syntax_to is set to _SYNTAX_CURRENT
        @return: converted text """

        if syntax_from == _SYNTAX_CURRENT:
            syntax_from = self.getCurrentSyntax(profile)
        if syntax_to == _SYNTAX_CURRENT:
            syntax_to = self.getCurrentSyntax(profile)
        syntaxes = TextSyntaxes.params_data['syntaxes']
        if syntax_from not in syntaxes:
            raise UnknownSyntax(syntax_from)
        if syntax_to not in syntaxes:
            raise UnknownSyntax(syntax_to)
        d = None

        if TextSyntaxes.OPT_NO_THREAD in syntaxes[syntax_from]["flags"]:
            d = syntaxes[syntax_from]["to"](text)
        else:
            d = deferToThread(syntaxes[syntax_from]["to"], text)

        #TODO: keep only body element and change it to a div here ?

        if safe:
            d.addCallback(self.clean_xhtml)

        if TextSyntaxes.OPT_NO_THREAD in syntaxes[syntax_to]["flags"]:
            d.addCallback(syntaxes[syntax_to]["from"])
        else:
            d.addCallback(lambda xhtml: deferToThread(syntaxes[syntax_to]["from"], xhtml))

        # converters can add new lines that disturb the microblog change detection
        d.addCallback(lambda text: text.rstrip())
        return d

    def addSyntax(self, name, to_xhtml_cb, from_xhtml_cb, flags = None):
        """ Add a new syntax to the manager
        @param name: unique name of the syntax
        @param to_xhtml_cb: callback to convert from syntax to XHTML
        @param from_xhtml_cb: callback to convert from XHTML to syntax
        @param flags: set of optional flags, can be:
            TextSyntaxes.OPT_DEFAULT: use as the default syntax (replace former one)
            TextSyntaxes.OPT_HIDDEN: do not show in parameters
            TextSyntaxes.OPT_NO_THREAD: do not defer to thread when converting (the callback must then return a deferred)

        """
        name = unicode(name)
        flags = flags or []
        if TextSyntaxes.OPT_HIDDEN in flags and TextSyntaxes.OPT_DEFAULT in flags:
            raise ValueError("%s and %s are mutually exclusive" % (TextSyntaxes.OPT_HIDDEN, TextSyntaxes.OPT_DEFAULT))

        syntaxes = TextSyntaxes.params_data['syntaxes']
        syntaxes[name] = {"to": to_xhtml_cb, "from": from_xhtml_cb, "flags": flags}
        if TextSyntaxes.OPT_DEFAULT in flags:
            syntaxes = TextSyntaxes.params_data['default'] = name

        self._updateParamOptions()

    def _removeMarkups(self, xhtml):
        """
        Remove XHTML markups from the given string.
        @param xhtml: the XHTML string to be cleaned
        @return: the cleaned string
        """
        cleaner = clean.Cleaner(kill_tags=['style'])
        cleaned = cleaner.clean_html(html.fromstring(xhtml))
        return html.tostring(cleaned, encoding=unicode, method="text")
