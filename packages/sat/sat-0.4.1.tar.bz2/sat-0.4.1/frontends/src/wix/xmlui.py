#!/usr/bin/python
# -*- coding: utf-8 -*-

# wix: a SAT frontend
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
import wx
from logging import debug, info, warning, error
from sat.tools.jid  import JID
from sat_frontends.tools import xmlui
from sat_frontends.constants import Const


class EventWidget(object):
    """ Used to manage change event of  widgets """

    def _xmluiOnChange(self, callback):
        """ Call callback with widget as only argument """
        def change_cb(event):
            callback(self)
        self.Bind(self._xmlui_change_event, change_cb)


class WixWidget(object):
    _xmlui_proportion = 0


class ValueWidget(WixWidget):
    def _xmluiGetValue(self):
        return self.GetValue()


class EmptyWidget(WixWidget, xmlui.EmptyWidget, wx.Window):

    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1)


class TextWidget(WixWidget, xmlui.TextWidget, wx.StaticText):

    def __init__(self, parent, value):
        wx.StaticText.__init__(self, parent, -1, value)


class LabelWidget(xmlui.LabelWidget, TextWidget):

    def __init__(self, parent, value):
        super(LabelWidget, self).__init__(parent, value+": ")


class JidWidget(xmlui.JidWidget, TextWidget):
    pass


class DividerWidget(WixWidget, xmlui.DividerWidget, wx.StaticLine):

    def __init__(self, parent, style='line'):
        wx.StaticLine.__init__(self, parent, -1)


class StringWidget(EventWidget, ValueWidget, xmlui.StringWidget, wx.TextCtrl):
    _xmlui_change_event = wx.EVT_TEXT

    def __init__(self, parent, value):
        wx.TextCtrl.__init__(self, parent, -1, value)
        self._xmlui_proportion = 1


class PasswordWidget(EventWidget, ValueWidget, xmlui.PasswordWidget, wx.TextCtrl):
    _xmlui_change_event = wx.EVT_TEXT

    def __init__(self, parent, value):
        wx.TextCtrl.__init__(self, parent, -1, value, style=wx.TE_PASSWORD)
        self._xmlui_proportion = 1


class TextBoxWidget(EventWidget, ValueWidget, xmlui.TextBoxWidget, wx.TextCtrl):
    _xmlui_change_event = wx.EVT_TEXT

    def __init__(self, parent, value):
        wx.TextCtrl.__init__(self, parent, -1, value, style=wx.TE_MULTILINE)
        self._xmlui_proportion = 1


class BoolWidget(EventWidget, ValueWidget, xmlui.BoolWidget, wx.CheckBox):
    _xmlui_change_event = wx.EVT_CHECKBOX

    def __init__(self, parent, state):
        wx.CheckBox.__init__(self, parent, -1, "", style=wx.CHK_2STATE)
        self.SetValue(state)
        self._xmlui_proportion = 1

    def _xmluiGetValue(self):
        return "true" if self.GetValue() else "false"


class ButtonWidget(EventWidget, WixWidget, xmlui.ButtonWidget, wx.Button):
    _xmlui_change_event = wx.EVT_BUTTON

    def __init__(self, parent, value, click_callback):
        wx.Button.__init__(self, parent, -1, value)
        self._xmlui_click_callback = click_callback
        parent.Bind(wx.EVT_BUTTON, lambda evt: click_callback(evt.GetEventObject()), self)

    def _xmluiOnClick(self, event):
        self._xmlui_click_callback(event.GetEventObject())
        event.Skip()

class ListWidget(EventWidget, WixWidget, xmlui.ListWidget, wx.ListBox):
    _xmlui_change_event = wx.EVT_LISTBOX

    def __init__(self, parent, options, flags):
        styles = wx.LB_MULTIPLE if not 'single' in flags else wx.LB_SINGLE
        wx.ListBox.__init__(self, parent, -1, choices=[option[1] for option in options], style=styles)
        self._xmlui_attr_map = {label: value for value, label in options}
        self._xmlui_proportion = 1

    def _xmluiSelectValue(self, value):
        try:
            label = [label for label, _value in self._xmlui_attr_map.items() if _value == value][0]
        except IndexError:
            warning(_("Can't find value [%s] to select" % value))
            return
        for idx in xrange(self.GetCount()):
            self.SetSelection(idx, self.GetString(idx) == label)

    def _xmluiGetSelectedValues(self):
        ret = []
        labels = [self.GetString(idx) for idx in self.GetSelections()]
        for label in labels:
            ret.append(self._xmlui_attr_map[label])
        return ret


class WixContainer(object):
    _xmlui_proportion = 1

    def _xmluiAppend(self, widget):
        self.sizer.Add(widget, self._xmlui_proportion, flag=wx.EXPAND)


class AdvancedListContainer(WixContainer, xmlui.AdvancedListContainer, wx.ScrolledWindow):

    def __init__(self, parent, columns, selectable='no'):
        wx.ScrolledWindow.__init__(self, parent)
        self._xmlui_selectable = selectable != 'no'
        if selectable:
            columns += 1
        self.sizer = wx.FlexGridSizer(cols=columns)
        self.SetSizer(self.sizer)
        self._xmlui_select_cb = None
        self._xmlui_select_idx = None
        self._xmlui_select_widgets = []

    def _xmluiAddRow(self, idx):
        # XXX: select_button is a Q&D way to implement row selection
        # FIXME: must be done properly
        if not self._xmlui_selectable:
            return
        select_button = wx.Button(self, wx.ID_OK, label=_("select"))
        self.sizer.Add(select_button)
        def click_cb(event, idx=idx):
            cb = self._xmlui_select_cb
            self._xmlui_select_idx = idx
            # TODO: fill self._xmlui_select_widgets
            if cb is not None:
                cb(self)
            event.Skip()
        self.Bind(wx.EVT_BUTTON, click_cb)

    def _xmluiGetSelectedWidgets(self):
        return self._xmlui_select_widgets

    def _xmluiGetSelectedIndex(self):
        return self._xmlui_select_idx

    def _xmluiOnSelect(self, callback):
        self._xmlui_select_cb = callback

class PairsContainer(WixContainer, xmlui.PairsContainer, wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.FlexGridSizer(cols=2)
        self.sizer.AddGrowableCol(1) #The growable column need most of time to be the right one in pairs
        self.SetSizer(self.sizer)


class TabsContainer(WixContainer, xmlui.TabsContainer, wx.Notebook):

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, -1, style=wx.NB_LEFT if self._xmlui_main.type=='param' else 0)

    def _xmluiAddTab(self, label):
        tab_panel = wx.Panel(self, -1)
        tab_panel.sizer = wx.BoxSizer(wx.VERTICAL)
        tab_panel.SetSizer(tab_panel.sizer)
        self.AddPage(tab_panel, label)
        VerticalContainer._xmluiAdapt(tab_panel)
        return tab_panel


class VerticalContainer(WixContainer, xmlui.VerticalContainer, wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)


class WidgetFactory(object):

    def __getattr__(self, attr):
        if attr.startswith("create"):
            cls = globals()[attr[6:]]
            cls._xmlui_main = self._xmlui_main
            return cls


class XMLUI(xmlui.XMLUI, wx.Frame):
    """Create an user interface from a SàT XML"""
    widget_factory = WidgetFactory()

    def __init__(self, host, xml_data, title=None, flags = None,):
        self.widget_factory._xmlui_main = self
        xmlui.XMLUI.__init__(self, host, xml_data, title, flags)

    def constructUI(self, xml_data):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX if 'NO_CANCEL' in self.flags else wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, None, style=style)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        def postTreat():
            if self.title:
                self.SetTitle(self.title)

            if self.type == 'form':
                dialogButtons = wx.StdDialogButtonSizer()
                submitButton = wx.Button(self.main_cont,wx.ID_OK, label=_("Submit"))
                dialogButtons.AddButton(submitButton)
                self.main_cont.Bind(wx.EVT_BUTTON, self.onFormSubmitted, submitButton)
                if not 'NO_CANCEL' in self.flags:
                    cancelButton = wx.Button(self.main_cont,wx.ID_CANCEL)
                    dialogButtons.AddButton(cancelButton)
                    self.main_cont.Bind(wx.EVT_BUTTON, self.onFormCancelled, cancelButton)
                dialogButtons.Realize()
                self.main_cont.sizer.Add(dialogButtons, flag=wx.ALIGN_CENTER_HORIZONTAL)

            self.sizer.Add(self.main_cont, 1, flag=wx.EXPAND)
            self.sizer.Fit(self)
            self.Show()

        super(XMLUI, self).constructUI(xml_data, postTreat)
        if not 'NO_CANCEL' in self.flags:
            self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.MakeModal()

    def _xmluiClose(self):
        self.MakeModal(False)
        self.Destroy()

    ###events

    def onParamChange(self, ctrl):
        super(XMLUI, self).onParamChange(ctrl)
        ### FIXME # Some hacks for better presentation, should be generic # FIXME ###
        param_name = ctrl._xmlui_name.split(Const.SAT_PARAM_SEPARATOR)[1]
        if (ctrl._param_category, param_name) == ('Connection', 'JabberID'):
            domain = JID(ctrl._xmluiGetValue()).domain
            for widget in (ctl['control'] for ctl in self.ctrl_list.values()):
                if (widget._param_category, widget._param_name) == ('Connection', 'Server'):
                    widget.SetValue(domain)
                    break

    def onFormSubmitted(self, event):
        """Called when submit button is clicked"""
        button = event.GetEventObject()
        super(XMLUI, self).onFormSubmitted(button)

    def onClose(self, event):
        """Close event: we have to send the form."""
        debug(_("close"))
        if self.type == 'param':
            self.onSaveParams()
        else:
            self._xmluiClose()
        event.Skip()

