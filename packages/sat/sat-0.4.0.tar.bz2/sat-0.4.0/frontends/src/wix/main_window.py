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
from sat_frontends.quick_frontend.quick_chat_list import QuickChatList
from sat_frontends.quick_frontend.quick_app import QuickApp
import wx
from sat_frontends.wix.contact_list import ContactList
from sat_frontends.wix.chat import Chat
from sat_frontends.wix.xmlui import XMLUI
from sat_frontends.wix.profile import Profile
from sat_frontends.wix.profile_manager import ProfileManager
import os.path
from sat.tools.jid  import JID
from logging import debug, info, warning, error
from sat_frontends.wix.constants import Const

idCONNECT,\
idDISCONNECT,\
idEXIT,\
idABOUT,\
idPARAM,\
idADD_CONTACT,\
idREMOVE_CONTACT,\
idSHOW_PROFILE,\
idJOIN_ROOM,\
= range(9)

class ChatList(QuickChatList):
    """This class manage the list of chat windows"""

    def createChat(self, target):
        return Chat(target, self.host)

class MainWindow(wx.Frame, QuickApp):
    """main app window"""

    def __init__(self):
        QuickApp.__init__(self)
        wx.Frame.__init__(self,None, title="SàT Wix", size=(350,500))

        #sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        #Frame elements
        self.contact_list = ContactList(self, self)
        self.contact_list.registerActivatedCB(self.onContactActivated)
        self.contact_list.Hide()
        self.sizer.Add(self.contact_list, 1, flag=wx.EXPAND)

        self.chat_wins=ChatList(self)
        self.CreateStatusBar()

        #ToolBar
        self.tools=self.CreateToolBar()
        self.statusBox = wx.ComboBox(self.tools, -1, "Online", choices=[status[1] for status in Const.PRESENCE],
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.tools.AddControl(self.statusBox)
        self.tools.AddSeparator()
        self.statusTxt = wx.TextCtrl(self.tools, -1, style=wx.TE_PROCESS_ENTER)
        self.tools.AddControl(self.statusTxt)
        self.Bind(wx.EVT_COMBOBOX, self.onStatusChange, self.statusBox)
        self.Bind(wx.EVT_TEXT_ENTER, self.onStatusChange, self.statusTxt)
        self.tools.Disable()

        #tray icon
        ticon = wx.Icon(os.path.join(self.media_dir, 'icons/crystal/32/tray_icon.xpm'), wx.BITMAP_TYPE_XPM)
        self.tray_icon = wx.TaskBarIcon()
        self.tray_icon.SetIcon(ticon, _("Wix jabber client"))
        wx.EVT_TASKBAR_LEFT_UP(self.tray_icon, self.onTrayClick)


        #events
        self.Bind(wx.EVT_CLOSE, self.onClose, self)

        #menus
        self.createMenus()
        for i in range(self.menuBar.GetMenuCount()):
            self.menuBar.EnableTop(i, False)

        #profile panel
        self.profile_pan = ProfileManager(self)
        self.sizer.Add(self.profile_pan, 1, flag=wx.EXPAND)

        self.postInit()

        self.Show()

    def plug_profile(self, profile_key='@DEFAULT@'):
        """Hide profile panel then plug profile"""
        debug (_('plugin profile %s' % profile_key))
        self.profile_pan.Hide()
        self.contact_list.Show()
        self.sizer.Layout()
        for i in range(self.menuBar.GetMenuCount()):
            self.menuBar.EnableTop(i, True)
        super(MainWindow, self).plug_profile(profile_key)

    def createMenus(self):
        info(_("Creating menus"))
        connectMenu = wx.Menu()
        connectMenu.Append(idCONNECT, _("&Connect	CTRL-c"),_(" Connect to the server"))
        connectMenu.Append(idDISCONNECT, _("&Disconnect	CTRL-d"),_(" Disconnect from the server"))
        connectMenu.Append(idPARAM,_("&Parameters"),_(" Configure the program"))
        connectMenu.AppendSeparator()
        connectMenu.Append(idABOUT, _("A&bout"), _(" About %s") % Const.APP_NAME)
        connectMenu.Append(idEXIT,_("E&xit"),_(" Terminate the program"))
        contactMenu = wx.Menu()
        contactMenu.Append(idADD_CONTACT, _("&Add contact"),_(" Add a contact to your list"))
        contactMenu.Append(idREMOVE_CONTACT, _("&Remove contact"),_(" Remove the selected contact from your list"))
        contactMenu.AppendSeparator()
        contactMenu.Append(idSHOW_PROFILE, _("&Show profile"), _(" Show contact's profile"))
        communicationMenu = wx.Menu()
        communicationMenu.Append(idJOIN_ROOM, _("&Join Room"),_(" Join a Multi-User Chat room"))
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(connectMenu,_("&General"))
        self.menuBar.Append(contactMenu,_("&Contacts"))
        self.menuBar.Append(communicationMenu,_("&Communication"))
        self.SetMenuBar(self.menuBar)

        #additionals menus
        #FIXME: do this in a more generic way (in quickapp)
        add_menus = self.bridge.getMenus('', Const.NO_SECURITY_LIMIT)
        for id_, type_, path, path_i18n  in add_menus:
            assert(type_=="NORMAL") #TODO: manage other types
            if len(path) != 2:
                raise NotImplementedError("Menu with a path != 2 are not implemented yet")
            category = path_i18n[0] # TODO: manage path with more than 2 levels
            name = path_i18n[1]
            menu_idx = self.menuBar.FindMenu(category)
            current_menu = None
            if menu_idx == wx.NOT_FOUND:
                #the menu is new, we create it
                current_menu = wx.Menu()
                self.menuBar.Append(current_menu, category)
            else:
                current_menu = self.menuBar.GetMenu(menu_idx)
            assert(current_menu != None)
            item_id = wx.NewId()
            help_string = self.bridge.getMenuHelp(id_, '')
            current_menu.Append(item_id, name, help=help_string)
            #now we register the event
            def event_answer(e, id_=id_):
                self.launchAction(id_, None, profile_key = self.profile)

            wx.EVT_MENU(self, item_id, event_answer)


        #events
        wx.EVT_MENU(self, idCONNECT, self.onConnectRequest)
        wx.EVT_MENU(self, idDISCONNECT, self.onDisconnectRequest)
        wx.EVT_MENU(self, idPARAM, self.onParam)
        wx.EVT_MENU(self, idABOUT, self.onAbout)
        wx.EVT_MENU(self, idEXIT, self.onExit)
        wx.EVT_MENU(self, idADD_CONTACT, self.onAddContact)
        wx.EVT_MENU(self, idREMOVE_CONTACT, self.onRemoveContact)
        wx.EVT_MENU(self, idSHOW_PROFILE, self.onShowProfile)
        wx.EVT_MENU(self, idJOIN_ROOM, self.onJoinRoom)

    def newMessage(self, from_jid, to_jid, msg, _type, extra, profile):
        QuickApp.newMessage(self, from_jid, to_jid, msg, _type, extra, profile)

    def showAlert(self, message):
        # TODO: place this in a separate class
        popup=wx.PopupWindow(self)
        ### following code come from wxpython demo
        popup.SetBackgroundColour("CADET BLUE")
        st = wx.StaticText(popup, -1, message, pos=(10,10))
        sz = st.GetBestSize()
        popup.SetSize( (sz.width+20, sz.height+20) )
        x=(wx.DisplaySize()[0]-popup.GetSize()[0])/2
        popup.SetPosition((x,0))
        popup.Show()
        wx.CallLater(5000,popup.Destroy)

    def showDialog(self, message, title="", type="info", answer_cb = None, answer_data = None):
        if type == 'info':
            flags = wx.OK | wx.ICON_INFORMATION
        elif type == 'error':
            flags = wx.OK | wx.ICON_ERROR
        elif type == 'yes/no':
            flags = wx.YES_NO | wx.ICON_QUESTION
        else:
            flags = wx.OK | wx.ICON_INFORMATION
            error(_('unmanaged dialog type: %s'), type)
        dlg = wx.MessageDialog(self, message, title, flags)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer_cb:
            data = [answer_data] if answer_data else []
            answer_cb(True if (answer == wx.ID_YES or answer == wx.ID_OK) else False, *data)

    def setStatusOnline(self, online=True, show="", statuses={}):
        """enable/disable controls, must be called when local user online status change"""
        if online:
            self.SetStatusText(Const.msgONLINE)
            self.tools.Enable()
            try:
                presence = [x for x in Const.PRESENCE if x[0] == show][0][1]
                self.statusBox.SetValue(presence)
            except (TypeError, IndexError):
                pass
            try:
                self.statusTxt.SetValue(statuses['default'])
            except (TypeError, KeyError):
                pass
        else:
            self.SetStatusText(Const.msgOFFLINE)
            self.tools.Disable()
        return

    def launchAction(self, callback_id, data=None, profile_key="@NONE@"):
        """ Launch a dynamic action
        @param callback_id: id of the action to launch
        @param data: data needed only for certain actions
        @param profile_key: %(doc_profile_key)s

        """
        if data is None:
            data = dict()
        def action_cb(data):
            if not data:
                # action was a one shot, nothing to do
                pass
            elif "xmlui" in data:
                debug (_("XML user interface received"))
                XMLUI(self, xml_data = data['xmlui'])
            else:
                dlg = wx.MessageDialog(self, _(u"Unmanaged action result"),
                                       _('Error'),
                                       wx.OK | wx.ICON_ERROR
                                      )
                dlg.ShowModal()
                dlg.Destroy()
        def action_eb(failure):
            dlg = wx.MessageDialog(self, unicode(failure),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()

        self.bridge.launchAction(callback_id, data, profile_key, callback=action_cb, errback=action_eb)

    def askConfirmation(self, confirmation_id, confirmation_type, data, profile):
        #TODO: refactor this in QuickApp
        if not self.check_profile(profile):
            return
        debug (_("Confirmation asked"))
        answer_data={}
        if confirmation_type == "FILE_TRANSFER":
            debug (_("File transfer confirmation asked"))
            dlg = wx.MessageDialog(self, _("The contact %(jid)s wants to send you the file %(filename)s\nDo you accept ?") % {'jid':data["from"], 'filename':data["filename"]},
                                   _('File Request'),
                                   wx.YES_NO | wx.ICON_QUESTION
                                  )
            answer=dlg.ShowModal()
            if answer==wx.ID_YES:
                filename = wx.FileSelector(_("Where do you want to save the file ?"), flags = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if filename:
                    answer_data["dest_path"] = filename
                    self.bridge.confirmationAnswer(confirmation_id, True, answer_data, profile)
                    self.waitProgress(confirmation_id, _("File Transfer"), _("Copying %s") % os.path.basename(filename), profile)
                else:
                    answer = wx.ID_NO
            if answer==wx.ID_NO:
                    self.bridge.confirmationAnswer(confirmation_id, False, answer_data, profile)

            dlg.Destroy()

        elif confirmation_type == "YES/NO":
            debug (_("Yes/No confirmation asked"))
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Confirmation'),
                                   wx.YES_NO | wx.ICON_QUESTION
                                  )
            answer=dlg.ShowModal()
            if answer==wx.ID_YES:
                self.bridge.confirmationAnswer(confirmation_id, True, {}, profile)
            if answer==wx.ID_NO:
                self.bridge.confirmationAnswer(confirmation_id, False, {}, profile)

            dlg.Destroy()

    def actionResult(self, type, id, data, profile):
        if not self.check_profile(profile):
            return
        debug (_("actionResult: type = [%(type)s] id = [%(id)s] data = [%(data)s]") % {'type':type, 'id':id, 'data':data})
        if not id in self.current_action_ids:
            debug (_('unknown id, ignoring'))
            return
        if type == "SUPPRESS":
            self.current_action_ids.remove(id)
        elif type == "SUCCESS":
            self.current_action_ids.remove(id)
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Success'),
                                   wx.OK | wx.ICON_INFORMATION
                                  )
            dlg.ShowModal()
            dlg.Destroy()
        elif type == "ERROR":
            self.current_action_ids.remove(id)
            dlg = wx.MessageDialog(self, data["message"],
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
        elif type == "XMLUI":
            self.current_action_ids.remove(id)
            debug (_("XML user interface received"))
            misc = {}
            #FIXME FIXME FIXME: must clean all this crap !
            title = _('Form')
            if data['type'] == _('registration'):
                title = _('Registration')
                misc['target'] = data['target']
                misc['action_back'] = self.bridge.gatewayRegister
            XMLUI(self, title=title, xml_data = data['xml'], misc = misc)
        elif type == "RESULT":
            self.current_action_ids.remove(id)
            if self.current_action_ids_cb.has_key(id):
                callback = self.current_action_ids_cb[id]
                del self.current_action_ids_cb[id]
                callback(data)
        elif type == "DICT_DICT":
            self.current_action_ids.remove(id)
            if self.current_action_ids_cb.has_key(id):
                callback = self.current_action_ids_cb[id]
                del self.current_action_ids_cb[id]
                callback(data)
        else:
            error (_("FIXME FIXME FIXME: type [%s] not implemented") % type)
            raise NotImplementedError



    def progressCB(self, progress_id, title, message, profile):
        data = self.bridge.getProgress(progress_id, profile)
        if data:
            if not self.pbar:
                #first answer, we must construct the bar
                self.pbar = wx.ProgressDialog(title, message, float(data['size']), None,
                    wx.PD_SMOOTH | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME)
                self.pbar.finish_value = float(data['size'])

            self.pbar.Update(int(data['position']))
        elif self.pbar:
            self.pbar.Update(self.pbar.finish_value)
            return

        wx.CallLater(10, self.progressCB, progress_id, title, message, profile)

    def waitProgress (self, progress_id, title, message, profile):
        self.pbar = None
        wx.CallLater(10, self.progressCB, progress_id, title, message, profile)



    ### events ###

    def onContactActivated(self, jid):
        debug (_("onContactActivated: %s"), jid)
        if self.chat_wins[jid.bare].IsShown():
            self.chat_wins[jid.bare].Hide()
        else:
            self.chat_wins[jid.bare].Show()

    def onConnectRequest(self, e):
        self.bridge.connect(self.profile)

    def onDisconnectRequest(self, e):
        self.bridge.disconnect(self.profile)

    def __updateStatus(self):
        show = [x for x in Const.PRESENCE if x[1] == self.statusBox.GetValue()][0][0]
        status = self.statusTxt.GetValue()
        self.bridge.setPresence(show=show, statuses={'default': status}, profile_key=self.profile)  #FIXME: manage multilingual statuses

    def onStatusChange(self, e):
        debug(_("Status change request"))
        self.__updateStatus()

    def onParam(self, e):
        debug(_("Param request"))
        def success(params):
            XMLUI(self, xml_data=params, title=_("Configuration"))

        def failure(error):
            dlg = wx.MessageDialog(self, unicode(error),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
        self.bridge.getParamsUI(app=Const.APP_NAME, profile_key=self.profile, callback=success, errback=failure)

    def onAbout(self, e):
        about = wx.AboutDialogInfo()
        about.SetName(Const.APP_NAME)
        about.SetVersion (unicode(self.bridge.getVersion()))
        about.SetCopyright(u"(C) 2009, 2010, 2011, 2012, 2013, 2014 Jérôme Poisson aka Goffi")
        about.SetDescription( _(u"%(name)s is a SàT (Salut à Toi) frontend\n"+
        u"%(name)s is based on WxPython, and is the standard graphic interface of SàT") % {'name': Const.APP_NAME})
        about.SetWebSite(("http://www.goffi.org", "Goffi's non-hebdo (french)"))
        about.SetDevelopers([ "Goffi (Jérôme Poisson)"])
        try:
            with open(Const.LICENCE_PATH, "r") as licence:
                about.SetLicence(''.join(licence.readlines()))
        except:
            pass

        wx.AboutBox(about)

    def onExit(self, e):
        self.Close()

    def onAddContact(self, e):
        debug(_("Add contact request"))
        dlg = wx.TextEntryDialog(
                self, _('Please enter new contact JID'),
                _('Adding a contact'), _('name@server.tld'))

        if dlg.ShowModal() == wx.ID_OK:
            jid=JID(dlg.GetValue())
            if jid.is_valid():
                self.bridge.addContact(jid.bare, profile_key=self.profile)
            else:
                error (_("'%s' is an invalid JID !"), jid)
                #TODO: notice the user

        dlg.Destroy()

    def onRemoveContact(self, e):
        debug(_("Remove contact request"))
        target = self.contact_list.getSelection()
        if not target:
            dlg = wx.MessageDialog(self, _("You haven't selected any contact !"),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _("Are you sure you want to delete %s from your roster list ?") % target.bare,
                               _('Contact suppression'),
                               wx.YES_NO | wx.ICON_QUESTION
                              )

        if dlg.ShowModal() == wx.ID_YES:
            info(_("Unsubscribing %s presence"), target.bare)
            self.bridge.delContact(target.bare, profile_key=self.profile)

        dlg.Destroy()

    def onShowProfile(self, e):
        debug(_("Show contact's profile request"))
        target = self.contact_list.getSelection()
        if not target:
            dlg = wx.MessageDialog(self, _("You haven't selected any contact !"),
                                   _('Error'),
                                   wx.OK | wx.ICON_ERROR
                                  )
            dlg.ShowModal()
            dlg.Destroy()
            return
        _id = self.bridge.getCard(target.bare, profile_key=self.profile)
        self.current_action_ids.add(_id)
        self.current_action_ids_cb[_id] = self.onProfileReceived

    def onProfileReceived(self, data):
        """Called when a profile is received"""
        debug (_('Profile received: [%s]') % data)
        profile=Profile(self, data)

    def onJoinRoom(self, e):
        warning('FIXME: temporary menu, must be improved')
        #TODO: a proper MUC room joining dialog with nickname etc
        dlg = wx.TextEntryDialog(
                self, _("Please enter MUC's JID"),
                #_('Entering a MUC room'), 'test@conference.necton2.int')
                _('Entering a MUC room'), 'room@muc_service.server.tld')
        if dlg.ShowModal() == wx.ID_OK:
            room_jid=JID(dlg.GetValue())
            if room_jid.is_valid():
                self.bridge.joinMUC(room_jid, self.profiles[self.profile]['whoami'].node, {}, self.profile)
            else:
                error (_("'%s' is an invalid JID !"), room_jid)

    def onClose(self, e):
        QuickApp.onExit(self)
        info(_("Exiting..."))
        for win in self.chat_wins:
            self.chat_wins[win].Destroy()
        self.tray_icon.Destroy()
        e.Skip()

    def onTrayClick(self, e):
        debug(_("Tray Click"))
        if self.IsShown():
            self.Hide()
        else:
            self.Show()
            self.Raise()
        e.Skip()

    def chatStateReceived(self, from_jid_s, state, profile):
        """Signal observer to display a contact chat state
        @param from_jid_s: contact who sent his new state
        @state: state
        @profile: current profile
        """
        print "TODO: chatStateReceived not implemented yet"
        pass
