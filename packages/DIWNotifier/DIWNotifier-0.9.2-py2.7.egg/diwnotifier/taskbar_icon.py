#Copyright (C) 2014 Marco Vespo
#
#DIW Notifier is free software; you can redistribute it and/or modify it
#under the terms of the GNU General Public Licence as published
#by the Free Software Foundation; either version 3 of the Licence,
#or (at your option) any later version.

#DIW Notifier is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
from settings import Settings

import logging
module_logger = logging.getLogger('diwnotifier.DIWNotifier.taskbar_icon')

import os
from utils import Thread, wrap
try:
    import wx
except ImportError:
    wx = None
    module_logger.error('Please install wx python module first')
    raise ImportError('Please install wx python module first')


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, app):
        super(TaskBarIcon, self).__init__()
        self.app = app
        self.update = False
        self.set_icon(Settings.TRAY_ICON, "")

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_profile)

        self.friendsc = self.notifyc = self.shoutboxc = self.msgc = "0"
        self.profile_link = ""
        self.pca_link = False
        self.pcm_link = False
        self.new_content = []

        self.quote_string = ""

        self.logger = logging.getLogger('diwnotifier.DIWNotifier.taskbar_icon.TaskBarIcon')
        self.logger.debug('creating an instance of diwnotifier.DIWNotifier.taskbar_icon.TaskBarIcon')

    #PASS
    def set_status(self, status):
        if status is "UPDATE":
            self.set_icon(Settings.TRAY_ICON, "")
            self.update = True
        elif status is "TOUPDATE":
            self.set_icon(Settings.TRAY_ICON, "\nTo Update...")
            self.update = False
        elif status is "OFFLINE":
            self.set_icon(Settings.TRAY_ICON_OFF, "\nOffline")
            self.update = False

    def CreatePopupMenu(self):
        menu = wx.Menu()
        if self.update:
            self.create_menu_item(menu, 'Profilo', None, "data/images/icons/profile.png", self.profile_link)
            menu.AppendSeparator()

            flags = [False, False]
            if self.pca_link:
                self.create_menu_item(menu, 'Amministrazione(PCA)', None, "data/images/icons/gears.png", self.pca_link)
                flags[0] = True

            if self.pcm_link:
                self.create_menu_item(menu, 'Moderazione(PCM)', None, "data/images/icons/gears.png", Settings.PCM_URL)
                flags[1] = True

            if flags[0]:
                self.create_menu_item(menu, 'Analytics', None, "data/images/icons/gears.png", Settings.PIWIK_URL)

            if flags[0] or flags[1]:
                menu.AppendSeparator()

            self.create_menu_item(menu, "Friends Online [" + self.friendsc + "]", None, "data/images/icons/friends.png",
                                  Settings.FRIENDS_URL)
            if self.msgc != "0":
                spam = "mail-mark-important.png"
            else:
                spam = "mail-message.png"
            self.create_menu_item(menu, "Messaggi [" + self.msgc + "]", None, "data/images/icons/" + spam,
                                  Settings.MSG_URL)
            menu.AppendSeparator()
            self.create_menu_item(menu, self.quote_string, None, "data/images/icons/mail-inbox.png", Settings.MSG_URL,
                                  False)
            menu.AppendSeparator()
            self.create_menu_item(
                menu, "Notifiche [" + self.notifyc + "]",
                None,
                "data/images/icons/notifications.png",
                Settings.NOTIFICATIONS_URL
            )
            self.create_menu_item(menu, "Shoutbox [" + self.shoutboxc + "]", None, "data/images/icons/shoutbox.png",
                                  Settings.SHOUTBOX_URL)
            menu.AppendSeparator()

            if not self.new_content:
                self.create_menu_item(menu, 'Loading new content...', None, None, None, False)

            for topic in self.new_content:
                self.create_menu_item(menu, topic.title, None, topic.dot_uri, topic.get_unread_link())
            menu.AppendSeparator()
            self.create_menu_item(menu, 'Reload', self.__su_do_batch, "data/images/icons/reload.png")
        else:
            self.create_menu_item(menu, "To update...", None, "data/images/icons/reload.png", None, False)
            menu.AppendSeparator()
        self.create_menu_item(menu, 'Preferenze', self.edit_preferences, "data/images/icons/preferences.png")
        menu.AppendSeparator()
        self.create_menu_item(menu, 'About', self.on_about_box, "data/images/icons/about.png")
        self.create_menu_item(menu, 'Quit', self.on_exit, "data/images/icons/quit.png")

        return menu

    def __su_do_batch(self, event):
        #self.set_status("TOUPDATE")#da errore
        self.logger.debug(str(event))
        self.update = False
        if not self.app.refresh_thread.isAlive():
            self.app.refresh_thread = Thread(self.app.update)
            self.app.queued_batch = False

    def set_icon(self, path, status=""):
        icon = wx.Icon(path, wx.BITMAP_TYPE_XPM, 24, 24)
        self.SetIcon(icon, Settings.APP_NAME + " " + Settings.APP_VERSION + "" + status)

    def on_about_box(self, event):
        self.logger.debug(str(event))
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(Settings.ABOUT_ICON, wx.BITMAP_TYPE_PNG))
        info.SetName(Settings.APP_NAME)
        info.SetVersion(Settings.APP_VERSION)
        info.SetDescription(Settings.DESCRIPTION)
        info.SetCopyright(Settings.COPYRIGHT)
        info.SetWebSite(Settings.WEBSITE)
        info.SetLicence(wrap(Settings.LICENSE, 300))
        info.AddDeveloper(Settings.DEVELOPER)
        info.AddDocWriter(Settings.DEVELOPER)
        info.AddArtist(Settings.ARTIST)
        wx.AboutBox(info)

    def on_exit(self, event):
        self.logger.debug(str(event))
        wx.CallAfter(self.Destroy)

    def open_link(self, url):
        self.logger.info(Settings.BROWSER + " " + url + "&")
        return os.popen(Settings.BROWSER + " " + url + "&")

    @staticmethod
    def edit_preferences(event):
        module_logger.debug(str(event))
        os.popen(Settings.EDITOR + " " + Settings.conf_path + " &")

    @staticmethod
    def on_profile(event):
        module_logger.debug(str(event))
        os.popen(Settings.BROWSER + " " + Settings.HOME_URL + " &")

    def create_menu_item(self, menu, label, function, icon, arg=None, enable=True):
        item = wx.MenuItem(menu, -1, label)
        if function is None:
            menu.Bind(wx.EVT_MENU, lambda event: self.open_link(arg), id=item.GetId())
        else:
            menu.Bind(wx.EVT_MENU, function, id=item.GetId())
        if not icon is None:
            img = wx.Image(Settings.app_home + '' + icon, wx.BITMAP_TYPE_PNG)
            item.SetBitmap(wx.BitmapFromImage(img))
        menu.AppendItem(item)

        if not enable:
            item.Enable(enable)

        return item

    def set_counters(self, friendsc, msgc, notifyc, shoutboxc):
        self.friendsc = friendsc
        self.msgc = msgc
        self.notifyc = notifyc
        self.shoutboxc = shoutboxc
