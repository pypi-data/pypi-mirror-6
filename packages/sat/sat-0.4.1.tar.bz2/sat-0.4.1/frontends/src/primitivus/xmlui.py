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
import urwid
from urwid_satext import sat_widgets
from logging import debug, info, warning, error
from xml.dom import minidom
from sat_frontends.tools import xmlui


class PrimitivusEvents(object):
    """ Used to manage change event of Primitivus widgets """

    def _event_callback(self, ctrl, *args, **ktkwargs):
        """" Call xmlui callback and ignore any extra argument """
        args[-1](ctrl)

    def _xmluiOnChange(self, callback):
        """ Call callback with widget as only argument """
        urwid.connect_signal(self, 'change', self._event_callback, callback)


class PrimitivusEmptyWidget(xmlui.EmptyWidget, urwid.Text):

    def __init__(self, parent):
        urwid.Text.__init__(self, '')


class PrimitivusTextWidget(xmlui.TextWidget, urwid.Text):

    def __init__(self, parent, value):
        urwid.Text.__init__(self, value)


class PrimitivusLabelWidget(xmlui.LabelWidget, PrimitivusTextWidget):

    def __init__(self, parent, value):
        super(PrimitivusLabelWidget, self).__init__(parent, value+": ")


class PrimitivusJidWidget(xmlui.JidWidget, PrimitivusTextWidget):
    pass


class PrimitivusDividerWidget(xmlui.DividerWidget, urwid.Divider):

    def __init__(self, parent, style='line'):
        if style == 'line':
            div_char = u'─'
        elif style == 'dot':
            div_char = u'·'
        elif style == 'dash':
            div_char = u'-'
        elif style == 'plain':
            div_char = u'█'
        elif style == 'blank':
            div_char = ' '
        else:
            warning(_("Unknown div_char"))
            div_char = u'─'

        urwid.Divider.__init__(self, div_char)

class PrimitivusStringWidget(xmlui.StringWidget, sat_widgets.AdvancedEdit, PrimitivusEvents):

    def __init__(self, parent, value):
        sat_widgets.AdvancedEdit.__init__(self, edit_text=value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusPasswordWidget(xmlui.PasswordWidget, sat_widgets.Password, PrimitivusEvents):

    def __init__(self, parent, value):
        sat_widgets.Password.__init__(self, edit_text=value)

    def _xmluiGetValue(self):
        return self.get_edit_text()


class PrimitivusTextBoxWidget(xmlui.TextBoxWidget, sat_widgets.AdvancedEdit, PrimitivusEvents):

    def __init__(self, parent, value):
        sat_widgets.AdvancedEdit.__init__(self, edit_text=value, multiline=True)

    def _xmluiGetValue(self):
        return self.getValue()


class PrimitivusBoolWidget(xmlui.BoolWidget, urwid.CheckBox, PrimitivusEvents):

    def __init__(self, parent, state):
        urwid.CheckBox.__init__(self, '', state = state)

    def _xmluiGetValue(self):
        return "true" if self.get_state() else "false"


class PrimitivusButtonWidget(xmlui.ButtonWidget, sat_widgets.CustomButton, PrimitivusEvents):

    def __init__(self, parent, value, click_callback):
        sat_widgets.CustomButton.__init__(self, value, on_press=click_callback)


class PrimitivusListWidget(xmlui.ListWidget, sat_widgets.List, PrimitivusEvents):

    def __init__(self, parent, options, flags):
        sat_widgets.List.__init__(self, options=options, style=flags)

    def _xmluiSelectValue(self, value):
        return self.selectValue(value)

    def _xmluiGetSelectedValues(self):
        return [option.value for option in self.getSelectedValues()]


class PrimitivusAdvancedListContainer(xmlui.AdvancedListContainer, sat_widgets.TableContainer, PrimitivusEvents):

    def __init__(self, parent, columns, selectable='no'):
        options = {'ADAPT':()}
        if selectable != 'no':
            options['HIGHLIGHT'] = ()
        sat_widgets.TableContainer.__init__(self, columns=columns, options=options, row_selectable = selectable!='no')

    def _xmluiAppend(self, widget):
        self.addWidget(widget)

    def _xmluiAddRow(self, idx):
        self.setRowIndex(idx)

    def _xmluiGetSelectedWidgets(self):
        return self.getSelectedWidgets()

    def _xmluiGetSelectedIndex(self):
        return self.getSelectedIndex()

    def _xmluiOnSelect(self, callback):
        """ Call callback with widget as only argument """
        urwid.connect_signal(self, 'click', self._event_callback, callback)

class PrimitivusPairsContainer(xmlui.PairsContainer, sat_widgets.TableContainer):

    def __init__(self, parent):
        options = {'ADAPT':(0,), 'HIGHLIGHT':(0,)}
        if self._xmlui_main.type == 'param':
            options['FOCUS_ATTR'] = 'param_selected'
        sat_widgets.TableContainer.__init__(self, columns=2, options=options)

    def _xmluiAppend(self, widget):
        if isinstance(widget, PrimitivusEmptyWidget):
            # we don't want highlight on empty widgets
            widget = urwid.AttrMap(widget, 'default')
        self.addWidget(widget)


class PrimitivusTabsContainer(xmlui.TabsContainer, sat_widgets.TabsContainer):

    def __init__(self, parent):
        sat_widgets.TabsContainer.__init__(self)

    def _xmluiAppend(self, widget):
        self.body.append(widget)

    def _xmluiAddTab(self, label):
        list_box = super(PrimitivusTabsContainer, self).addTab(label)
        if hasattr(PrimitivusVerticalContainer, "_PrimitivusVerticalContainer__super"): # workaround for Urwid's metaclass baviour
                del PrimitivusVerticalContainer._PrimitivusVerticalContainer__super
        PrimitivusVerticalContainer._xmluiAdapt(list_box)
        return list_box


class PrimitivusVerticalContainer(xmlui.VerticalContainer, urwid.ListBox):

    def __init__(self, parent):
        urwid.ListBox.__init__(self, urwid.SimpleListWalker([]))

    def _xmluiAppend(self, widget):
        self.body.append(widget)


class WidgetFactory(object):

    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()["Primitivus" + attr[6:]] # XXX: we prefix with "Primitivus" to work around an Urwid bug, WidgetMeta in Urwid don't manage multiple inheritance with same names
            cls._xmlui_main = self._xmlui_main
            return cls

class XMLUI(xmlui.XMLUI, urwid.WidgetWrap):
    widget_factory = WidgetFactory()

    def __init__(self, host, xml_data, title = None, flags = None):
        self.widget_factory._xmlui_main = self
        self._dest = None
        xmlui.XMLUI.__init__(self, host, xml_data, title, flags)
        urwid.WidgetWrap.__init__(self, self.main_cont)

    def constructUI(self, xml_data):
        def postTreat():
            assert self.main_cont.body

            if isinstance(self.main_cont.body[0],sat_widgets.TabsContainer):
                self._main_cont = self.main_cont.body[0] #xxx: awfull hack cause TabsContainer is a BoxWidget, can't be inside a ListBox

            if self.type == 'form':
                buttons = []
                buttons.append(urwid.Button(_('Submit'),self.onFormSubmitted))
                if not 'NO_CANCEL' in self.flags:
                    buttons.append(urwid.Button(_('Cancel'),self.onFormCancelled))
                max_len = max([len(button.get_label()) for button in buttons])
                grid_wid = urwid.GridFlow(buttons,max_len+4,1,0,'center')
                self.main_cont.body.append(grid_wid)
            elif self.type == 'param':
                assert(isinstance(self.main_cont,sat_widgets.TabsContainer))
                buttons = []
                buttons.append(sat_widgets.CustomButton(_('Save'),self.onSaveParams))
                buttons.append(sat_widgets.CustomButton(_('Cancel'),lambda x:self.host.removeWindow()))
                max_len = max([button.getSize() for button in buttons])
                grid_wid = urwid.GridFlow(buttons,max_len,1,0,'center')
                self.main_cont.addFooter(grid_wid)

        super(XMLUI, self).constructUI(xml_data, postTreat)
        urwid.WidgetWrap.__init__(self, self.main_cont)

    def show(self, show_type=None, valign='middle'):
        """Show the constructed UI
        @param show_type: how to show the UI:
            - None (follow XMLUI's recommendation)
            - 'popup'
            - 'window'
        @param valign: vertical alignment when show_type is 'popup'.
                       Ignored when show_type is 'window'.

        """
        if show_type is None:
            if self.type in ('window', 'param'):
                show_type = 'window'
            elif self.type in ('popup', 'form'):
                show_type = 'popup'

        if show_type not in ('popup', 'window'):
            raise ValueError('Invalid show_type [%s]' % show_type)

        self._dest = show_type
        decorated = sat_widgets.LabelLine(self, sat_widgets.SurroundedText(self.title or ''))
        if show_type == 'popup':
            self.host.showPopUp(decorated, valign=valign)
        elif show_type == 'window':
            self.host.addWindow(decorated)
        else:
            assert(False)
        self.host.redraw()


    def _xmluiClose(self):
        if self._dest == 'window':
            self.host.removeWindow()
        else:
            self.host.removePopUp()
