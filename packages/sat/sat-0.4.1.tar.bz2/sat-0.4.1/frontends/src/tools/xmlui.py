#!/usr/bin/python
# -*- coding: utf-8 -*-

# SàT frontend tools
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
from sat_frontends.constants import Const
from sat.core.exceptions import DataError


class InvalidXMLUI(Exception):
    pass


def getText(node):
    """Get child text nodes
    @param node: dom Node
    @return: joined unicode text of all nodes

    """
    data = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            data.append(child.wholeText)
    return u"".join(data)


class Widget(object):
    """ base Widget """
    pass


class EmptyWidget(Widget):
    """ Just a placeholder widget """
    pass


class TextWidget(Widget):
    """ Non interactive text """
    pass


class LabelWidget(Widget):
    """ Non interactive text """
    pass


class JidWidget(Widget):
    """ Jabber ID """
    pass


class DividerWidget(Widget):
    """ Separator """
    pass


class StringWidget(Widget):
    """ Input widget with require a string
    often called Edit in toolkits

    """


class PasswordWidget(Widget):
    """ Input widget with require a masked string

    """


class TextBoxWidget(Widget):
    """ Input widget with require a long, possibly multilines string
    often called TextArea in toolkits

    """


class BoolWidget(Widget):
    """ Input widget with require a boolean value
    often called CheckBox in toolkits

    """


class ButtonWidget(Widget):
    """ A clickable widget """


class ListWidget(Widget):
    """ A widget able to show/choose one or several strings in a list """


class Container(Widget):
    """ Widget which can contain other ones with a specific layout """

    @classmethod
    def _xmluiAdapt(cls, instance):
        """ Make cls as instance.__class__
        cls must inherit from original instance class
        Usefull when you get a class from UI toolkit

        """
        assert instance.__class__ in cls.__bases__
        instance.__class__ = type(cls.__name__, cls.__bases__, dict(cls.__dict__))


class PairsContainer(Container):
    """ Widgets are disposed in rows of two (usually label/input) """
    pass


class TabsContainer(Container):
    """ A container which several other containers in tabs
    Often called Notebook in toolkits

    """


class VerticalContainer(Container):
    """ Widgets are disposed vertically """
    pass


class AdvancedListContainer(Container):
    """ Widgets are disposed in rows with advaned features """
    pass


class XMLUI(object):
    """ Base class to construct SàT XML User Interface
    New frontends can inherite this class to easily implement XMLUI
    @property widget_factory: factory to create frontend-specific widgets
    @proporety dialog_factory: factory to create frontend-specific dialogs

    """
    widget_factory = None
    dialog_factory = None # TODO

    def __init__(self, host, xml_data, title = None, flags = None, dom_parse=None, dom_free=None):
        """ Initialise the XMLUI instance
        @param host: %(doc_host)s
        @param xml_data: the raw XML containing the UI
        @param title: force the title, or use XMLUI one if None
        @param flags: list of string which can be:
            - NO_CANCEL: the UI can't be cancelled
        @param dom_parse: methode equivalent to minidom.parseString (but which  must manage unicode), or None to use default one
        @param dom_free: method used to free the parsed DOM

        """
        if dom_parse is None:
            from xml.dom import minidom
            self.dom_parse = lambda xml_data: minidom.parseString(xml_data.encode('utf-8'))
            self.dom_free = lambda cat_dom: cat_dom.unlink()
        else:
            self.dom_parse = dom_parse
            self.dom_free = dom_free or (lambda cat_dom: None)
        self.host = host
        self.title = title or ""
        if flags is None:
            flags = []
        self.flags = flags
        self.ctrl_list = {}  # usefull to access ctrl
        self._main_cont = None
        self.constructUI(xml_data)

    def escape(self, name):
        """ return escaped name for forms """
        return u"%s%s" % (Const.SAT_FORM_PREFIX, name)

    @property
    def main_cont(self):
        return self._main_cont

    @main_cont.setter
    def main_cont(self, value):
        if self._main_cont is not None:
            raise ValueError(_("XMLUI can have only one main container"))
        self._main_cont = value


    def _parseChilds(self, parent, current_node, wanted = ('container',), data = None):
        """ Recursively parse childNodes of an elemen
        @param parent: widget container with '_xmluiAppend' method
        @param current_node: element from which childs will be parsed
        @param wanted: list of tag names that can be present in the childs to be SàT XMLUI compliant
        @param data: additionnal data which are needed in some cases

        """
        for node in current_node.childNodes:
            if wanted and not node.nodeName in wanted:
                raise InvalidXMLUI('Unexpected node: [%s]' % node.nodeName)

            if node.nodeName == "container":
                type_ = node.getAttribute('type')
                if parent is self and type_ != 'vertical':
                    # main container is not a VerticalContainer and we want one, so we create one to wrap it
                    parent = self.widget_factory.createVerticalContainer(self)
                    self.main_cont = parent
                if type_ == "tabs":
                    cont = self.widget_factory.createTabsContainer(parent)
                    self._parseChilds(parent, node, ('tab',), cont)
                elif type_ == "vertical":
                    cont = self.widget_factory.createVerticalContainer(parent)
                    self._parseChilds(cont, node, ('widget', 'container'))
                elif type_ == "pairs":
                    cont = self.widget_factory.createPairsContainer(parent)
                    self._parseChilds(cont, node, ('widget', 'container'))
                elif type_ == "advanced_list":
                    try:
                        columns = int(node.getAttribute('columns'))
                    except (TypeError, ValueError):
                        raise DataError("Invalid columns")
                    selectable = node.getAttribute('selectable') or 'no'
                    auto_index = node.getAttribute('auto_index') == 'true'
                    data = {'index': 0} if auto_index else None
                    cont = self.widget_factory.createAdvancedListContainer(parent, columns, selectable)
                    callback_id = node.getAttribute("callback") or None
                    if callback_id is not None:
                        if selectable == 'no':
                            raise ValueError("can't have selectable=='no' and callback_id at the same time")
                        cont._xmlui_callback_id = callback_id
                        cont._xmluiOnSelect(self.onAdvListSelect)

                    self._parseChilds(cont, node, ('row',), data)
                else:
                    print(_("Unknown container [%s], using default one") % type_)
                    cont = self.widget_factory.createVerticalContainer(parent)
                    self._parseChilds(cont, node, ('widget', 'container'))
                try:
                    parent._xmluiAppend(cont)
                except (AttributeError, TypeError): # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                    if parent is self:
                        self.main_cont = cont
                    else:
                        raise Exception(_("Internal Error, container has not _xmluiAppend method"))

            elif node.nodeName == 'tab':
                name = node.getAttribute('name')
                label = node.getAttribute('label')
                if not name or not isinstance(data, TabsContainer):
                    raise InvalidXMLUI
                if self.type == 'param':
                    self._current_category = name #XXX: awful hack because params need category and we don't keep parent
                tab_cont = data
                new_tab = tab_cont._xmluiAddTab(label or name)
                self._parseChilds(new_tab, node, ('widget', 'container'))

            elif node.nodeName == 'row':
                try:
                    index = str(data['index'])
                    data['index'] += 1
                except TypeError:
                    index = node.getAttribute('index') or None
                parent._xmluiAddRow(index)
                self._parseChilds(parent, node, ('widget', 'container'))

            elif node.nodeName == "widget":
                id_ = node.getAttribute("id")
                name = node.getAttribute("name")
                type_ = node.getAttribute("type")
                value = node.getAttribute("value") if node.hasAttribute('value') else u''
                if type_=="empty":
                    ctrl = self.widget_factory.createEmptyWidget(parent)
                elif type_=="text":
                    try:
                        value = node.childNodes[0].wholeText
                    except IndexError:
                        # warning (_("text node has no child !"))
                        pass # FIXME proper warning (this one is not OK with Libervia)
                    ctrl = self.widget_factory.createTextWidget(parent, value)
                elif type_=="label":
                    ctrl = self.widget_factory.createLabelWidget(parent, value)
                elif type_=="jid":
                    ctrl = self.widget_factory.createJidWidget(parent, value)
                elif type_=="divider":
                    style = node.getAttribute("style") or 'line'
                    ctrl = self.widget_factory.createDividerWidget(parent, style)
                elif type_=="string":
                    ctrl = self.widget_factory.createStringWidget(parent, value)
                    self.ctrl_list[name] = ({'type':type_, 'control':ctrl})
                elif type_=="password":
                    ctrl = self.widget_factory.createPasswordWidget(parent, value)
                    self.ctrl_list[name] = ({'type':type_, 'control':ctrl})
                elif type_=="textbox":
                    ctrl = self.widget_factory.createTextBoxWidget(parent, value)
                    self.ctrl_list[name] = ({'type':type_, 'control':ctrl})
                elif type_=="bool":
                    ctrl = self.widget_factory.createBoolWidget(parent, value=='true')
                    self.ctrl_list[name] = ({'type':type_, 'control':ctrl})
                elif type_=="list":
                    style=[] if node.getAttribute("multi")=='yes' else ['single']
                    _options = [(option.getAttribute("value"), option.getAttribute("label")) for option in node.getElementsByTagName("option")]
                    ctrl = self.widget_factory.createListWidget(parent, _options, style)
                    ctrl._xmluiSelectValue(node.getAttribute("value"))
                    self.ctrl_list[name] = ({'type':type_, 'control':ctrl})
                elif type_=="button":
                    callback_id = node.getAttribute("callback")
                    ctrl = self.widget_factory.createButtonWidget(parent, value, self.onButtonPress)
                    ctrl._xmlui_param_id = (callback_id,[field.getAttribute('name') for field in node.getElementsByTagName("field_back")])
                else:
                    print(_("FIXME FIXME FIXME: widget type [%s] is not implemented") % type_)
                    raise NotImplementedError(_("FIXME FIXME FIXME: type [%s] is not implemented") % type_)

                if self.type == 'param' and type_ != 'text':
                    try:
                        ctrl._xmluiOnChange(self.onParamChange)
                        ctrl._param_category = self._current_category
                    except (AttributeError, TypeError): # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                        if not isinstance(ctrl, (EmptyWidget, TextWidget, LabelWidget, JidWidget)):
                            print(_("No change listener on [%s]") % ctrl)

                ctrl._xmlui_name = name
                parent._xmluiAppend(ctrl)

            else:
                raise NotImplementedError(_('Unknown tag [%s]') % node.nodeName)

    def constructUI(self, xml_data, post_treat=None):
        """ Actually construct the UI
        @param xml_data: raw XMLUI
        @param post_treat: frontend specific treatments to do once the UI is constructed
        @return: constructed widget
        """
        cat_dom = self.dom_parse(xml_data)
        top=cat_dom.documentElement
        self.type = top.getAttribute("type")
        self.title = self.title or top.getAttribute("title") or u""
        self.session_id = top.getAttribute("session_id") or None
        self.submit_id = top.getAttribute("submit") or None
        if top.nodeName != "sat_xmlui" or not self.type in ['form', 'param', 'window', 'popup']:
            raise InvalidXMLUI

        if self.type == 'param':
            self.param_changed = set()

        self._parseChilds(self, cat_dom.documentElement)

        if post_treat is not None:
            post_treat()

        self.dom_free(cat_dom)

    def _xmluiClose(self):
        """ Close the window/popup/... where the constructeur XMLUI is
        this method must be overrided

        """
        raise NotImplementedError

    def _xmluiLaunchAction(self, action_id, data):
        self.host.launchAction(action_id, data, profile_key = self.host.profile)

    def _xmluiSetParam(self, name, value, category):
        self.host.bridge.setParam(name, value, category, profile_key=self.host.profile)

    ##EVENTS##

    def onParamChange(self, ctrl):
        """ Called when type is param and a widget to save is modified
        @param ctrl: widget modified

        """
        assert(self.type == "param")
        self.param_changed.add(ctrl)

    def onAdvListSelect(self, ctrl):
        data = {}
        widgets = ctrl._xmluiGetSelectedWidgets()
        for wid in widgets:
            try:
                name = self.escape(wid._xmlui_name)
                value = wid._xmluiGetValue()
                data[name] = value
            except (AttributeError, TypeError): # XXX: TypeError is here because pyjamas raise a TypeError instead of an AttributeError
                pass
        idx = ctrl._xmluiGetSelectedIndex()
        if idx is not None:
            data['index'] = idx
        callback_id = ctrl._xmlui_callback_id
        if callback_id is None:
            print(_("No callback_id found"))
            return
        self._xmluiLaunchAction(callback_id, data)

    def onButtonPress(self, button):
        """ Called when an XMLUI button is clicked
        Launch the action associated to the button
        @param button: the button clicked

        """
        callback_id, fields = button._xmlui_param_id
        data = {}
        for field in fields:
            escaped = self.escape(field)
            ctrl = self.ctrl_list[field]
            if isinstance(ctrl['control'], ListWidget):
                data[escaped] = u'\t'.join(ctrl['control']._xmluiGetSelected())
            else:
                data[escaped] = ctrl['control']._xmluiGetValue()
        self._xmluiLaunchAction(callback_id, data)

    def onFormSubmitted(self, ignore=None):
        """ An XMLUI form has been submited
        call the submit action associated with this form

        """
        selected_values = []
        for ctrl_name in self.ctrl_list:
            escaped = self.escape(ctrl_name)
            ctrl = self.ctrl_list[ctrl_name]
            if isinstance(ctrl['control'], ListWidget):
                selected_values.append((escaped, u'\t'.join(ctrl['control']._xmluiGetSelectedValues())))
            else:
                selected_values.append((escaped, ctrl['control']._xmluiGetValue()))
        if self.submit_id is not None:
            data = dict(selected_values)
            if self.session_id is not None:
                data["session_id"] = self.session_id
            self._xmluiLaunchAction(self.submit_id, data)

        else:
            print(_("The form data is not sent back, the type is not managed properly"))
        self._xmluiClose()

    def onFormCancelled(self, ignore=None):
        """ Called when a form is cancelled """
        print(_("Cancelling form"))
        self._xmluiClose()

    def onSaveParams(self, ignore=None):
        """ Params are saved, we send them to backend
        self.type must be param

        """
        assert(self.type == 'param')
        for ctrl in self.param_changed:
            if isinstance(ctrl, ListWidget):
                value = u'\t'.join(ctrl._xmluiGetSelectedValues())
            else:
                value = ctrl._xmluiGetValue()
            param_name = ctrl._xmlui_name.split(Const.SAT_PARAM_SEPARATOR)[1]
            self._xmluiSetParam(param_name, value, ctrl._param_category)

        self._xmluiClose()
