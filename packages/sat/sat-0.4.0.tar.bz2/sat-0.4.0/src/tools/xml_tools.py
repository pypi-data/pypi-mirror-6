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
from logging import debug, info, error, warning
from xml.dom import minidom, NotFoundErr
from wokkel import data_form
from twisted.words.xish import domish
from sat.core import exceptions

"""This library help manage XML used in SàT (parameters, registration, etc) """

SAT_FORM_PREFIX = "SAT_FORM_"
SAT_PARAM_SEPARATOR = "_XMLUI_PARAM_" # used to have unique elements names


# Helper functions

def _dataFormField2XMLUIData(field):
    """ Get data needed to create an XMLUI's Widget from Wokkel's data_form's Field
    field can be modified (if it's fixed and it has no value)
    @param field: data_form.Field (it uses field.value, field.fieldType, field.label and field.var)
    @return: widget_type, widget_args, widget_kwargs

    """
    widget_args = [field.value]
    widget_kwargs = {}
    if field.fieldType == 'fixed' or field.fieldType is None:
        widget_type = 'text'
        if field.value is None:
            if field.label is None:
                warning(_("Fixed field has neither value nor label, ignoring it"))
                field.value = ""
            else:
                field.value = field.label
                field.label = None
            widget_args[0] = field.value
    elif field.fieldType == 'text-single':
        widget_type = "string"
    elif field.fieldType == 'text-private':
        widget_type = "password"
    elif field.fieldType == 'boolean':
        widget_type = "bool"
        if widget_args[0] is None:
            widget_args[0] = 'false'
    elif field.fieldType == 'list-single':
        widget_type = "list"
        del widget_args[0]
        widget_kwargs["options"] = [(option.value, option.label or option.value) for option in field.options]
    else:
        error(u"FIXME FIXME FIXME: Type [%s] is not managed yet by SàT" % field.fieldType)
        widget_type = "string"

    if field.var:
        widget_kwargs["name"] = field.var

    return widget_type, widget_args, widget_kwargs


def dataForm2XMLUI(form, submit_id, session_id=None):
    """Take a data form (xep-0004, Wokkel's implementation) and convert it to a SàT XML
    @param submit_id: callback id to call when submitting form
    @param session_id: id to return with the data

    """
    form_ui = XMLUI("form", "vertical", submit_id=submit_id, session_id=session_id)

    if form.instructions:
        form_ui.addText('\n'.join(form.instructions), 'instructions')

    form_ui.changeContainer("pairs")

    for field in form.fieldList:
        widget_type, widget_args, widget_kwargs = _dataFormField2XMLUIData(field)
        label = field.label or field.var
        if label:
            form_ui.addLabel(label)
        else:
            form_ui.addEmpty()

        form_ui.addWidget(widget_type, *widget_args, **widget_kwargs)

    return form_ui

def dataFormResult2AdvancedList(xmlui, form_xml):
    """Take a raw data form (not parsed by XEP-0004) and convert it to an advanced list
    raw data form is used because Wokkel doesn't manage result items parsing yet
    @param xmlui: the XMLUI where the AdvancedList will be added
    @param form_xml: domish.Element of the data form
    @return: AdvancedList element
    """
    headers = {}
    try:
        reported_elt = form_xml.elements('jabber:x:data', 'reported').next()
    except StopIteration:
        raise exceptions.DataError("Couldn't find expected <reported> tag")

    for elt in reported_elt.elements():
        if elt.name != "field":
            raise exceptions.DataError("Unexpected tag")
        name = elt["var"]
        label = elt.attributes.get('label','')
        type_ = elt.attributes.get('type')
        headers[name] = (label, type_)

    if not headers:
        raise exceptions.DataError("No reported fields (see XEP-0004 §3.4)")

    adv_list = AdvancedListContainer(xmlui, headers=headers, columns=len(headers), parent=xmlui.current_container)
    xmlui.changeContainer(adv_list)

    item_elts = form_xml.elements('jabber:x:data', 'item')

    for item_elt in item_elts:
        for elt in item_elt.elements():
            if elt.name != 'field':
                warning("Unexpected tag (%s)" % elt.name)
                continue
            field = data_form.Field.fromElement(elt)

            widget_type, widget_args, widget_kwargs = _dataFormField2XMLUIData(field)
            xmlui.addWidget(widget_type, *widget_args, **widget_kwargs)

    return xmlui

def dataFormResult2XMLUI(form_xml, session_id=None):
    """Take a raw data form (not parsed by XEP-0004) and convert it to a SàT XMLUI
    raw data form is used because Wokkel doesn't manage result items parsing yet
    @param form_xml: domish.Element of the data form
    @return: XMLUI interface
    """

    xmlui = XMLUI("window", "vertical", session_id=session_id)
    dataFormResult2AdvancedList(xmlui, form_xml)
    return xmlui

def XMLUIResult2DataFormResult(xmlui_data):
    """ Extract form data from a XMLUI return
    @xmlui_data: data returned by frontends for XMLUI form
    @return: dict of data usable by Wokkel's dataform
    """
    return {key[len(SAT_FORM_PREFIX):]: value for key, value in xmlui_data.iteritems() if key.startswith(SAT_FORM_PREFIX)}

def formEscape(name):
    """ Return escaped name for forms """
    return u"%s%s"  % (SAT_FORM_PREFIX, name)

def XMLUIResultToElt(xmlui_data):
    """ Construct result domish.Element from XMLUI result
    @xmlui_data: data returned by frontends for XMLUI form
    """
    form = data_form.Form('submit')
    form.makeFields(XMLUIResult2DataFormResult(xmlui_data))
    return form.toElement()

def tupleList2dataForm(values):
    """convert a list of tuples (name,value) to a wokkel submit data form"""
    form = data_form.Form('submit')
    for value in values:
        field = data_form.Field(var=value[0], value=value[1])
        form.addField(field)

    return form

def paramsXML2XMLUI(xml):
    """Convert the xml for parameter to a SàT XML User Interface"""
    params_doc = minidom.parseString(xml.encode('utf-8'))
    top = params_doc.documentElement
    if top.nodeName != 'params':
        raise exceptions.DataError(_('INTERNAL ERROR: parameters xml not valid'))

    param_ui = XMLUI("param", "tabs")
    tabs_cont = param_ui.current_container

    for category in top.getElementsByTagName("category"):
        category_name = category.getAttribute('name')
        label = category.getAttribute('label')
        if not category_name:
            raise exceptions.DataError(_('INTERNAL ERROR: params categories must have a name'))
        tabs_cont.addTab(category_name, label=label, container=PairsContainer)
        for param in category.getElementsByTagName("param"):
            widget_kwargs = {}

            param_name = param.getAttribute('name')
            param_label = param.getAttribute('label')
            type_ = param.getAttribute('type')
            if not param_name and type_ != 'text':
                raise exceptions.DataError(_('INTERNAL ERROR: params must have a name'))

            value = param.getAttribute('value') or None
            callback_id = param.getAttribute('callback_id') or None

            if type_ == 'list':
                options = _getParamListOptions(param)
                widget_kwargs['options'] = options

            if type_ in ("button", "text"):
                param_ui.addEmpty()
                value = param_label
            else:
                param_ui.addLabel(param_label or param_name)

            if value:
                widget_kwargs["value"] = value

            if callback_id:
                widget_kwargs['callback_id'] = callback_id

            widget_kwargs['name'] = "%s%s%s" % (category_name, SAT_PARAM_SEPARATOR, param_name)

            param_ui.addWidget(type_, **widget_kwargs)

    return param_ui.toXml()


def _getParamListOptions(param):
    """Retrieve the options for list element. Allow listing the <option/>
    tags directly in <param/> or in an intermediate <options/> tag."""
    elems = param.getElementsByTagName("options")
    if len(elems) == 0:
        elems = param.getElementsByTagName("option")
    else:
        elems = elems.item(0).getElementsByTagName("option")
    if len(elems) == 0:
        return []
    return [elem.getAttribute("value") for elem in elems]


## XMLUI Elements


class Element(object):
    """ Base XMLUI element """
    type = None

    def __init__(self, xmlui, parent=None):
        """Create a container element
        @param xmlui: XMLUI instance
        @parent: parent element
        """
        assert(self.type) is not None
        if not hasattr(self, 'elem'):
            self.elem = parent.xmlui.doc.createElement(self.type)
        self.xmlui = xmlui
        if parent is not None:
            parent.append(self)
        self.parent = parent

    def append(self, child):
        self.elem.appendChild(child.elem)
        child.parent = self


class TopElement(Element):
    """ Main XML Element """
    type = 'top'

    def __init__(self, xmlui):
        self.elem = xmlui.doc.documentElement
        super(TopElement, self).__init__(xmlui)


class TabElement(Element):
    """ Used by TabsContainer to give name and label to tabs """
    type = 'tab'

    def __init__(self, parent, name, label):
        if not isinstance(parent, TabsContainer):
            raise exceptions.DataError(_("TabElement must be a child of TabsContainer"))
        super(TabElement, self).__init__(parent.xmlui, parent)
        self.elem.setAttribute('name', name)
        self.elem.setAttribute('label', label)


class FieldBackElement(Element):
    """ Used by ButtonWidget to indicate which field have to be sent back """
    type = 'field_back'

    def __init__(self, parent, name):
        assert(isinstance(parent, ButtonWidget))
        super(FieldBackElement, self).__init__(parent.xmlui, parent)
        self.elem.setAttribute('name', name)


class OptionElement(Element):
    """" Used by ListWidget to specify options """
    type = 'option'

    def __init__(self, parent, option):
        assert(isinstance(parent, ListWidget))
        super(OptionElement, self).__init__(parent.xmlui, parent)
        if isinstance(option, basestring):
            value, label = option, option
        elif isinstance(option, tuple):
            value, label = option
        self.elem.setAttribute('value', value)
        self.elem.setAttribute('label', label)


class RowElement(Element):
    """" Used by AdvancedListContainer """
    type = 'row'

    def __init__(self, parent):
        assert(isinstance(parent, AdvancedListContainer))
        super(RowElement, self).__init__(parent.xmlui, parent)
        if parent.next_row_idx is not None:
            if parent.auto_index:
                raise exceptions.DataError(_("Can't set row index if auto_index is True"))
            self.elem.setAttribute('index', parent.next_row_idx)
            parent.next_row_idx = None


class HeaderElement(Element):
    """" Used by AdvancedListContainer """
    type = 'header'

    def __init__(self, parent, name=None, label=None, description=None):
        """
        @param parent: AdvancedListContainer instance
        @param name: name of the container
        @param label: label to be displayed in columns
        @param description: long descriptive text

        """
        assert(isinstance(parent, AdvancedListContainer))
        super(HeaderElement, self).__init__(parent.xmlui, parent)
        if name:
            self.elem.setAttribute('name', name)
        if label:
            self.elem.setAttribute('label', label)
        if description:
            self.elem.setAttribute('description', description)


class Container(Element):
    """ And Element which contains other ones and has a layout """
    type = None

    def __init__(self, xmlui, parent=None):
        """Create a container element
        @param xmlui: XMLUI instance
        @parent: parent element or None
        """
        self.elem = xmlui.doc.createElement('container')
        super(Container, self).__init__(xmlui, parent)
        self.elem.setAttribute('type', self.type)

    def getParentContainer(self):
        """ Return first parent container
        @return: parent container or None

        """
        current = self.parent
        while(not isinstance(current, (Container)) and
              current is not None):
            current = current.parent
        return current

class VerticalContainer(Container):
    type = "vertical"


class HorizontalContainer(Container):
    type = "horizontal"


class PairsContainer(Container):
    type = "pairs"


class TabsContainer(Container):
    type = "tabs"

    def addTab(self, name, label=None, container=VerticalContainer):
        """Add a tab"""
        if not label:
            label = name
        tab_elt = TabElement(self, name, label)
        new_container = container(self.xmlui, tab_elt)
        self.xmlui.changeContainer(new_container)

    def end(self):
        """ Called when we have finished tabs
        change current container to first container parent

        """
        parent_container = self.getParentContainer()
        self.xmlui.changeContainer(parent_container)


class AdvancedListContainer(Container):
    type = "advanced_list"

    def __init__(self, xmlui, callback_id=None, name=None, headers=None, items=None, columns=None, selectable = 'no', auto_index = False, parent=None):
        """Create an advanced list
        @param headers: optional headers informations
        @param callback_id: id of the method to call when selection is done
        @param items: list of widgets to add (just the first row)
        @param columns: number of columns in this table, or None to autodetect
        @param selectable: one of:
            'no': nothing is done
            'single': one row can be selected
        @param auto_index: if True, indexes will be generated by frontends, starting from 0
        @return: created element
        """
        assert selectable in ('no', 'single')
        if not items and columns is None:
            raise exceptions.DataError(_("either items or columns need do be filled"))
        if headers is None:
            headers = []
        if items is None:
            items = []
        super(AdvancedListContainer, self).__init__(xmlui, parent)
        if columns is None:
            columns = len(items[0])
        self._columns = columns
        self._item_idx = 0
        self.current_row = None
        if headers:
            if len(headers) != self._columns:
                raise exceptions.DataError(_("Headers lenght doesn't correspond to columns"))
            self.addHeaders(headers)
        if items:
            self.addItems(items)
        self.elem.setAttribute('columns', str(self._columns))
        if callback_id is not None:
            self.elem.setAttribute('callback', callback_id)
        self.elem.setAttribute('selectable', selectable)
        self.auto_index = auto_index
        if auto_index:
            self.elem.setAttribute('auto_index', 'true')
        self.next_row_idx = None

    def addHeaders(self, headers):
        for header in headers:
            self.addHeader(header)

    def addHeader(self, header):
        pass # TODO

    def addItems(self, items):
        for item in items:
            self.append(item)

    def setRowIndex(self, idx):
        """ Set index for next row
        index are returned when a row is selected, in data's "index" key
        @param idx: string index to associate to the next row

        """
        self.next_row_idx = idx

    def append(self, child):
        if isinstance(child, RowElement):
            return super(AdvancedListContainer, self).append(child)
        if self._item_idx % self._columns == 0:
            self.current_row = RowElement(self)
        self.current_row.append(child)
        self._item_idx += 1

    def end(self):
        """ Called when we have finished list
        change current container to first container parent

        """
        if self._item_idx % self._columns != 0:
            raise exceptions.DataError(_("Incorrect number of items in list"))
        parent_container = self.getParentContainer()
        self.xmlui.changeContainer(parent_container)


class Widget(Element):
    type = None

    def __init__(self, xmlui, name=None, parent=None):
        """Create an element
        @param xmlui: XMLUI instance
        @param name: name of the element or None
        @param parent: parent element or None
        """
        self.elem = xmlui.doc.createElement('widget')
        super(Widget, self).__init__(xmlui, parent)
        if name:
            self.elem.setAttribute('name', name)
        self.elem.setAttribute('type', self.type)


class InputWidget(Widget):
    pass


class EmptyWidget(Widget):
    type = 'empty'


class TextWidget(Widget):
    type = 'text'

    def __init__(self, xmlui, value, name=None, parent=None):
        super(TextWidget, self).__init__(xmlui, name, parent)
        text = self.xmlui.doc.createTextNode(value)
        self.elem.appendChild(text)


class LabelWidget(Widget):
    type='label'

    def __init__(self, xmlui, label, name=None, parent=None):
        super(LabelWidget, self).__init__(xmlui, name, parent)
        self.elem.setAttribute('value', label)


class JidWidget(Widget):
    type='jid'

    def __init__(self, xmlui, jid, name=None, parent=None):
        super(JidWidget, self).__init__(xmlui, name, parent)
        try:
            self.elem.setAttribute('value', jid.full())
        except AttributeError:
            self.elem.setAttribute('value', unicode(jid))


class DividerWidget(Widget):
    type = 'divider'

    def __init__(self, xmlui, style='line', name=None, parent=None):
        """ Create a divider
        @param xmlui: XMLUI instance
        @param style: one of:
            - line: a simple line
            - dot: a line of dots
            - dash: a line of dashes
            - plain: a full thick line
            - blank: a blank line/space
        @param name: name of the widget
        @param parent: parent container

        """
        super(DividerWidget, self).__init__(xmlui, name, parent)
        self.elem.setAttribute('style', style)


class StringWidget(InputWidget):
    type = 'string'

    def __init__(self, xmlui, value=None, name=None, parent=None):
        super(StringWidget, self).__init__(xmlui, name, parent)
        if value:
            self.elem.setAttribute('value', value)


class PasswordWidget(StringWidget):
    type = 'password'


class TextBoxWidget(StringWidget):
    type = 'textbox'


class BoolWidget(InputWidget):
    type = 'bool'

    def __init__(self, xmlui, value='false', name=None, parent=None):
        if value == '0':
            value='false'
        elif value == '1':
            value='true'
        if not value in ('true', 'false'):
            raise exceptions.DataError(_("Value must be 0, 1, false or true"))
        super(BoolWidget, self).__init__(xmlui, name, parent)
        self.elem.setAttribute('value', value)


class ButtonWidget(Widget):
    type = 'button'

    def __init__(self, xmlui, callback_id, value=None, fields_back=None, name=None, parent=None):
        """Add a button
        @param callback_id: callback which will be called if button is pressed
        @param value: label of the button
        @fields_back: list of names of field to give back when pushing the button
        @param name: name
        @param parent: parent container
        """
        if fields_back is None:
            fields_back = []
        super(ButtonWidget, self).__init__(xmlui, name, parent)
        self.elem.setAttribute('callback', callback_id)
        if value:
            self.elem.setAttribute('value', value)
        for field in fields_back:
            fback_el = FieldBackElement(self, field)


class ListWidget(InputWidget):
    type = 'list'

    def __init__(self, xmlui, options, value=None, style=None, name=None, parent=None):
        if style is None:
            style = set()
        styles = set(style)
        if not options:
            warning(_('empty "options" list'))
        if not styles.issubset(['multi']):
            raise exceptions.DataError(_("invalid styles"))
        super(ListWidget, self).__init__(xmlui, name, parent)
        self.addOptions(options)
        if value:
            self.elem.setAttribute('value', value)
        for style in styles:
            self.elem.setAttribute(style, 'yes')

    def addOptions(self, options):
        """i Add options to a multi-values element (e.g. list) """
        for option in options:
            OptionElement(self, option)


## XMLUI main class


class XMLUI(object):
    """This class is used to create a user interface (form/window/parameters/etc) using SàT XML"""

    def __init__(self, panel_type="window", container="vertical", title=None, submit_id=None, session_id=None):
        """Init SàT XML Panel
        @param panel_type: one of
            - window (new window)
            - popup
            - form (formulaire, depend of the frontend, usually a panel with cancel/submit buttons)
            - param (parameters, presentation depend of the frontend)
        @param container: disposition of elements, one of:
            - vertical: elements are disposed up to bottom
            - horizontal: elements are disposed left to right
            - pairs: elements come on two aligned columns
              (usually one for a label, the next for the element)
            - tabs: elemens are in categories with tabs (notebook)
        @param title: title or default if None
        @param submit_id: callback id to call for panel_type we can submit (form, param)
        """
        self._introspect()
        if panel_type not in ['window', 'form', 'param', 'popup']:
            raise exceptions.DataError(_("Unknown panel type [%s]") % panel_type)
        if panel_type == 'form' and submit_id is None:
            raise exceptions.DataError(_("form XMLUI need a submit_id"))
        if not isinstance(container, basestring):
            raise exceptions.DataError(_("container argument must be a string"))
        self.type = panel_type
        impl = minidom.getDOMImplementation()

        self.doc = impl.createDocument(None, "sat_xmlui", None)
        top_element = self.doc.documentElement
        top_element.setAttribute("type", panel_type)
        if title:
            top_element.setAttribute("title", title)
        self.submit_id = submit_id
        self.session_id = session_id
        self.main_container  = self._createContainer(container, TopElement(self))
        self.current_container = self.main_container

    def _introspect(self):
        """ Introspect module to find Widgets and Containers """
        self._containers = {}
        self._widgets = {}
        for obj in globals().values():
            try:
                if issubclass(obj, Widget):
                    if obj.__name__ == 'Widget':
                        continue
                    self._widgets[obj.type] = obj
                elif issubclass(obj, Container):
                    if obj.__name__ == 'Container':
                        continue
                    self._containers[obj.type] = obj
            except TypeError:
                pass

    def __del__(self):
        self.doc.unlink()

    def __getattr__(self, name):
        if name.startswith("add") and name not in ('addWidget',): # addWidgetName(...) create an instance of WidgetName
            class_name = name[3:]+"Widget"
            if class_name in globals():
                cls = globals()[class_name]
                if issubclass(cls, Widget):
                    def createWidget(*args, **kwargs):
                        if "parent" not in kwargs:
                            kwargs["parent"] = self.current_container
                        if "name" not in kwargs and issubclass(cls, InputWidget): # name can be given as first argument or in keyword arguments for InputWidgets
                            args = list(args)
                            kwargs["name"] = args.pop(0)
                        return cls(self, *args, **kwargs)
                    return createWidget
        return object.__getattribute__(self, name)

    @property
    def submit_id(self):
        top_element = self.doc.documentElement
        value = top_element.getAttribute("submit")
        return value or None

    @submit_id.setter
    def submit_id(self, value):
        top_element = self.doc.documentElement
        if value is None:
            try:
                top_element.removeAttribute("submit")
            except NotFoundErr:
                pass
        elif value: # submit_id can be the empty string to bypass form restriction
            top_element.setAttribute("submit", value)

    @property
    def session_id(self):
        top_element = self.doc.documentElement
        value = top_element.getAttribute("session_id")
        return value or None

    @session_id.setter
    def session_id(self, value):
        top_element = self.doc.documentElement
        if value is None:
            try:
                top_element.removeAttribute("session_id")
            except NotFoundErr:
                pass
        elif value:
            top_element.setAttribute("session_id", value)
        else:
            raise exceptions.DataError("session_id can't be empty")

    def _createContainer(self, container, parent=None, **kwargs):
        """Create a container element
        @param type: container type (cf init doc)
        @parent: parent element or None
        """
        if container not in self._containers:
            raise exceptions.DataError(_("Unknown container type [%s]") % container)
        cls = self._containers[container]
        new_container = cls(self, parent=parent, **kwargs)
        return new_container

    def changeContainer(self, container, **kwargs):
        """Change the current container
        @param container: either container type (container it then created),
                          or an Container instance"""
        if isinstance(container, basestring):
            self.current_container = self._createContainer(container, self.current_container.getParentContainer() or self.main_container, **kwargs)
        else:
            self.current_container = self.main_container if container is None else container
        assert(isinstance(self.current_container, Container))
        return self.current_container

    def addWidget(self, type_, *args, **kwargs):
        """Convenience method to add an element"""
        if type_ not in self._widgets:
            raise exceptions.DataError(_("Invalid type [%s]") % type_)
        if "parent" not in kwargs:
            kwargs["parent"] = self.current_container
        cls = self._widgets[type_]
        return cls(self, *args, **kwargs)

    def toXml(self):
        """return the XML representation of the panel"""
        return self.doc.toxml()


# Misc other funtions


class ElementParser(object):
    """callable class to parse XML string into Element
    Found at http://stackoverflow.com/questions/2093400/how-to-create-twisted-words-xish-domish-element-entirely-from-raw-xml/2095942#2095942
    (c) Karl Anderson"""

    def __call__(self, string):
        self.result = None

        def onStart(elem):
            self.result = elem

        def onEnd():
            pass

        def onElement(elem):
            self.result.addChild(elem)

        parser = domish.elementStream()
        parser.DocumentStartEvent = onStart
        parser.ElementEvent = onElement
        parser.DocumentEndEvent = onEnd
        tmp = domish.Element((None, "s"))
        tmp.addRawXml(string.replace('\n', ' ').replace('\t', ' '))
        parser.parse(tmp.toXml().encode('utf-8'))
        return self.result.firstChildElement()
