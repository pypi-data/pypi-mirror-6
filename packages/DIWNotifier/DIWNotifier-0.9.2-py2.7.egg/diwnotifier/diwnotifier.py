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
import pynotify
import sys
import os
import copy

from scraping import Session, WebParser

from settings import Settings
Settings.collector.save()

from utils import MyConfigParser, download_avatar, ShortLinksCollector, bool_print, ThreadsCollector, Thread, which,\
    check_notification_daemon

from taskbar_icon import TaskBarIcon, wx

import warnings
warnings.filterwarnings(action="ignore", message=".*gzip transfer encoding is experimental!", category=UserWarning)

import logging
import logging.handlers

logging.basicConfig()

module_logger = logging.getLogger('diwnotifier')
module_logger.setLevel(Settings.LOG_LEVEL)




class DIWNotifier(wx.App):

    def OnInit(self):
        try:
            self.queued_batch = False
            self.first = True

            self.config = MyConfigParser(Settings.conf_path)
            self.config.report_bug_at = Settings.EMAIL

            #LOGGER BLOCK
            ###############
            self.logger = logging.getLogger('diwnotifier.DIWNotifier')

            # create a file handler
            log_path = Settings.log_dir + self.config.read_field("credentials", "user") + ".log"
            handler = logging.FileHandler(log_path)
            handler.setLevel(logging.INFO)

            # create a logging format
            formatter = logging.Formatter(Settings.LOG_FORMATTING)
            handler.setFormatter(formatter)

            # add the handlers to the logger
            self.logger.addHandler(handler)

            # set log rotate
            self.logger.addHandler(logging.handlers.RotatingFileHandler(log_path, maxBytes=2097152, backupCount=100))

            self.collector = ShortLinksCollector(Settings.links_collector_uri)
            self.collector.load()

            # notification daemon check
            if not check_notification_daemon():
                self.logger.warn("No active notification daemon")
                if which("/usr/lib/notification-daemon/notification-daemon"):
                    self.logger.warn("try with /usr/lib/notification-daemon/notification-daemon")
                    try:
                        os.popen("/usr/lib/notification-daemon/notification-daemon&")
                    except:
                        print "Error loading subprocess."
                        Settings.NOTIFICATIONS = False
                    else:
                        self.logger.warn("done ...")
                else:
                    Settings.NOTIFICATIONS = False

            self.count = {'friends': ['0', '0'], 'msgs': ['0', '0'], 'notify': ['0', '0'], 'shoutbox': ['0', '0']}

            self.tbi = TaskBarIcon(self)

            if not pynotify.init("clandiw_systray"):
                self.logger.error('pynotify.init error, notifications will be disabled')
                Settings.NOTIFICATIONS = False

            #LOGIN
            ########
            self.session = Session()
            user = self.config.read_field("credentials", "user",)
            pw = self.config.read_field("credentials", "passwd")

            if bool_print("Login to " + Settings.LOGIN_URL, self.session.login, Settings.LOGIN_URL, user, pw):
                self.logger.info('Hello ' + user + '!')
            else:
                self.logger.error('\tError message: ' + self.session.login_status)
                #LOGIN FAILED NOTIFY
                ############
                error_msg = 'Error message: ' + \
                            self.session.login_status +\
                            '.\n' + 'Watch <a href=\'file://' + log_path + '\'>' + log_path + '</a> for more info'

                self.notify(Settings.HOME_URL + ' - Login failed ',
                            error_msg, Settings.app_home+'data/images/dramma.png', Settings.T1)
                return False

            self.parser = WebParser()
            self.refresh_thread = Thread(self.update)
        except Exception, err:
            sys.stderr.write('ERROR: %s\n' % str(err))
            return False
        return True

    #ARGV SWITCH
    ####################################
    @staticmethod
    def argv_check():
        if sys.argv[1] == '-h':
            print(Settings.APP_NAME + ', version ' + Settings.APP_VERSION)
            print('Usage:')
            print('diwnotifier [options]')
            print('Options:')
            print('  -e : Edit configuration file')
            print('  -h : Display this help message and exit')
            print('  -v : Display version number and exit')
            print('  -a : Make autostart file')
            sys.exit(0)
        if sys.argv[1] == '-v':
            print(Settings.APP_NAME + ', version %s' % Settings.APP_VERSION)
            sys.exit(0)
        if sys.argv[1] == '-e':
            os.popen(Settings.EDITOR + " " + Settings.conf_path)
            sys.exit(0)
        if sys.argv[1] == '-a':
            DIWNotifier.make_autostart()
            sys.exit(0)

    @staticmethod
    def make_autostart():
        os.popen("gksu ln -s " + Settings.app_home + "/images/clandiw.png /usr/share/pixmaps/clandiw.png 2> /dev/null")
        write = '''[Desktop Entry]
        Type=Application
        Exec=diwnotifier
        Icon=clandiw
        Hidden=false
        NoDisplay=false
        X-GNOME-Autostart-enabled=true
        Name[it_IT]=DIW Notifier
        Name=DIW Notifier
        Comment=a featureful web crawler for http://clandiw.it site'''
        autostart_desktop = open(Settings.autostart_path, "w+")
        autostart_desktop.write(write)
        autostart_desktop.close()
        module_logger.info("[*] " + Settings.autostart_path + " created...")

    def counts_refresh(self):
        self.count['friends'][0] = self.tbi.friendsc
        self.count['friends'][1] = self.parser.get_notification_count(
            'title="Friends Online"><span class=\'ipsHasNotifications\'>')

        self.count['msgs'][0] = self.tbi.msgc
        self.count['msgs'][1] = self.parser.get_unread_msgs_count()

        self.count['notify'][0] = self.tbi.notifyc
        self.count['notify'][1] = self.parser.get_notification_count(
            ('title="Notifiche"><img src="http://clandiw.it/public/style_images/brave/clear.gif" alt="" />'
             '<span class=\'ipsHasNotifications\'>'))

        self.count['shoutbox'][1] = self.parser.get_notification_count(
            'id="shoutbox-tab-count" class="ipsHasNotifications" style="display: none;">')

    def tbi_refresh(self):
        #TBI UPDATING
        ##############
        if self.first:
            self.tbi.profile_link = self.parser.get_link(Settings.MSG_URL, 'Tuo Profilo')
        #--------------------
            self.tbi.pca_link = self.parser.get_link(Settings.MSG_URL,
                                                     'Pannello di Controllo degli Amministratori (PCA)')
            self.tbi.pcm_link = self.parser.get_link(Settings.MSG_URL,
                                                     'Pannello di Controllo dei Moderatori (PCM)')
        #--------------------
        self.tbi.set_counters(self.count['friends'][1],
                              self.count['msgs'][1],
                              self.count['notify'][1],
                              self.count['shoutbox'][1])
        #--------------------
        self.tbi.quote_string = self.parser.get_quote_string()

    def __load_page(self, url):
        return self.parser.add_page(self.session.get_page(url))

    def load_and_notify(self):
        self.parser.clean_pages()

        bool_print("LOAD " + self.collector.mirror(Settings.MSG_URL), self.__load_page(Settings.MSG_URL))

        if self.first:
            Settings.image_uri = download_avatar(self.parser.get_main_avatar(), Settings.avatars_path)

        self.counts_refresh()

        self.tbi_refresh()

        if not self.tbi.update:
            self.tbi.update = True

        threads = ThreadsCollector(
            self.notify_from_msg_page,
            self.notify_from_friends_page,
            self.notify_from_notifications_page,
            self.shoutbox_notify,
            self.update_new_content()
        )
        threads.make()
        threads.start_all()
        #threads.join_all()

    def update_new_content(self):
        bool_print("LOAD " + self.collector.mirror(Settings.NEW_CONTENT),
                   self.__load_page(Settings.NEW_CONTENT))

        self.tbi.new_content = self.parser.get_new_content()

    def notify(self, title, body, image=Settings.avatars_path + 'default_large.png', timeout=Settings.T2):
        if Settings.NOTIFICATIONS:
            n = pynotify.Notification(title, body, image)
            n.set_timeout(timeout)
            if not n.show():
                self.logger.warn('Failed to send ' + title + ' notification')
                return False
            self.logger.info('TITLE:' + title + '\nBODY:\n' + body)
            return True
        return False

    def notify_from_msg_page(self):
        #MAIN NOTIFY
        #############
        if self.first:
            self.notify(Settings.HOME_URL,
                        "<a href='" + Settings.FRIENDS_URL + "'>Friends</a>:" + self.count['friends'][1] +
                        "\n<a href='" + Settings.MSG_URL + "'>Unread messages</a>:" + self.count['msgs'][1] +
                        "\n<a href='" + Settings.NOTIFICATIONS_URL + "'>Notifications:</a>" + self.count['notify'][1] +
                        "\n<a href='" + Settings.SHOUTBOX_URL + "'>Shoutbox</a>:" + self.count['shoutbox'][1] + "",
                        Settings.image_uri, Settings.T1)

        #MSG NOTIFY
        ############
        msg = self.config.read_field("notifications", "messages")
        if self.count['msgs'][0] != self.count['msgs'][1] and self.count['msgs'][1] != "0" and msg == "True":
            msg_data = self.parser.get_last_msg_detail()
            msg_data['what_link'] = self.collector.add(msg_data['what_link'])
            self.notify(Settings.HOME_URL + " - " + self.count['msgs'][1] + " unread messages ",
                        "Last from <a href='" + msg_data['who_link'] + "'>" + msg_data['who'] + "</a>\n" +
                        msg_data['when'] + ": <a href='" + msg_data['what_link'] + "'>" + msg_data['what'] + "</a>",
                        msg_data['avatar'], Settings.T2)

    def notify_from_friends_page(self):
        if self.config.read_field("notifications", "friends") == "True":
            bool_print("LOAD " + self.collector.mirror(Settings.FRIENDS_URL),
                       self.__load_page(Settings.FRIENDS_URL))

            #FRIENDS NOTIFY
            ################
            if self.count['friends'][0] != self.count['friends'][1] and self.count['friends'][1] != "0":
                friends_online = self.parser.get_friends_online(self.count['friends'][1])

                string = ""
                for name, profile in friends_online.items():
                    string += "<a href='" + self.collector.add(profile) + "'>" + name + "</a>, "

                self.notify(Settings.HOME_URL + " - " + self.count['friends'][1] + " Friends online",
                            string[:-2],
                            Settings.image_uri, Settings.T2)

    def notify_from_notifications_page(self):
        if self.config.read_field("notifications", "notifications") == "True":
            bool_print("LOAD " + self.collector.mirror(Settings.NOTIFICATIONS_URL),
                       self.__load_page(Settings.NOTIFICATIONS_URL))

            #LAST NOTIFICATION
            ###################
            if self.count['notify'][0] != self.count['notify'][1] and self.count['notify'][1] != "0":
                self.ln = self.parser.get_last_notification()
                self.notify(Settings.HOME_URL + " - " + self.tbi.notifyc + " new notifications",
                            self.ln['when'] + ":" + self.ln['what'],
                            self.ln['avatar'], Settings.T2)

    def shoutbox_notify(self):
        #SHOUTBOX NOTIFY
        #################
        if self.config.read_field("notifications", "shoutbox") == "True":
            eggs = copy.deepcopy(self.parser.last_shout)

            self.parser.get_last_shout()

            flag = False
            for key, value in eggs.iteritems():
                if eggs[key] != self.parser.last_shout[key]:
                    flag = True

            if flag and self.parser.last_shout['what'] != "":
                self.notify(Settings.HOME_URL + " - Last Shout",
                            "@" + self.parser.last_shout['who'] + "\n" +
                            "<a href='" + Settings.SHOUTBOX_URL + "'>" + self.parser.last_shout['what'] + "</a>\n" +
                            self.parser.last_shout['when'],
                            self.parser.last_shout['avatar'], Settings.T2)

    def update(self):
        self.logger.info('Update...')

        self.load_and_notify()

        if self.first:
            self.first = False
            self.Bind(wx.EVT_IDLE, self.on_idle)

        self.collector.save()

    def on_idle(self, event, time=Settings.REFRESH_TIME):
        self.logger.debug(str(event))
        if not self.queued_batch:
            self.logger.debug("on_idle OK")
            wx.CallLater(time, self.do_batch)
            self.queued_batch = True
            self.logger.debug("on_idle exit")

    def do_batch(self):
        self.logger.debug("do_batch")
        if not self.refresh_thread.isAlive():
            self.refresh_thread = Thread(self.update)
            self.queued_batch = False
        self.logger.debug("do_batch exit")


def main():
    try:
        if len(sys.argv) > 1:
            DIWNotifier.argv_check()
        app = DIWNotifier()
        app.MainLoop()
    except KeyboardInterrupt:
        module_logger.info('Exiting program...')
        sys.exit(1)

if __name__ == '__main__':
    main()
