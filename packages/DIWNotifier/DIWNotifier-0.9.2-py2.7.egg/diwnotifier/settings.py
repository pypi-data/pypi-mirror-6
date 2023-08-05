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
from utils import os, ShortLinksCollector, MyConfigParser
import getpass
stuff_dir = os.getenv("HOME") + unicode("/.diwnotifier/")
conf_path = stuff_dir + unicode("etc/diwnotifier.conf")
if os.path.isdir(stuff_dir + unicode("etc/")):
    try:
        with open(conf_path):
            pass
    except IOError:
        print "Userid/Email:",
        user = raw_input()
        pswd = getpass.getpass("Password:")
        write = '''[credentials]
user = ''' + user + '''
passwd = ''' + pswd + '''

[notifications]
friends=True
messages=True
notifications=True
shoutbox=True

#MILLISECONDS
#########################
[time]
refresh=90000
#NOTIFICATION TIMEOUT
#########################
main=5000
message=10000'''
        conf = open(conf_path, "w+")
        conf.write(write)
        conf.close()
        print("[*] " + conf_path + " created...")


class Settings:

    APP_NAME = 'DIW Notifier'
    APP_VERSION = '0.9.2'

    EMAIL = 'am0n@clandiw.it'

    HOME_URL = 'http://clandiw.it'
    LOGIN_URL = 'http://clandiw.it/index.php?app=core\&module=global&section=login'
    SHOUTBOX_URL = 'http://clandiw.it/index.php?/shoutbox/'

    app_home = unicode("/usr/local/lib/python2.7/dist-packages/DIWNotifier-0.9.2-py2.7.egg/diwnotifier/")
    #app_home = os.getcwd() + '/'
    #ICONS
    #######
    icons_path = app_home + unicode('data/images/icons/')

    TRAY_ICON_MAIN = icons_path + 'clandiw.xpm'
    TRAY_ICON = icons_path + 'clandiw.xpm'
    TRAY_ICON_OFF = icons_path + 'clandiw_off.xpm'

    #SHORT LINK COLLECTOR
    ######################
    links_collector_uri = stuff_dir + unicode("var/cache/short_links_collector.txt")

    collector = ShortLinksCollector(links_collector_uri)
    collector.load()

    #LINKS
    #######
    MSG_URL = collector.add("http://clandiw.it/index.php?app=members&module=messaging")
    FRIENDS_URL = collector.add("http://clandiw.it/index.php?app=members&module=friendsonline")
    NOTIFICATIONS_URL = collector.add(
        "http://clandiw.it/index.php?app=core&module=usercp&tab=core&area=notificationlog")
    NEW_CONTENT = collector.add(("http://clandiw.it/index.php?app=core&module=search&do=viewNewContent&search_app="
                                "forums&sid=2a4e1257c3e3566f5f623a86709fa4f8&search_app_filters[forums][searchInKey]="
                                "&change=1&period=week&userMode=all&followedItemsOnly=0"))
    PCM_URL = 'http://clandiw.it/index.php?app=core\\&module=modcp'
    PIWIK_URL = HOME_URL + '/analytics'
    avatars_path = stuff_dir + unicode("var/cache/avatars/")
    image_uri = avatars_path + unicode('default_large.png')
    conf_path = stuff_dir + unicode("etc/diwnotifier.conf")

    autostart_path = os.getenv("HOME") + unicode("/.config/autostart/diwnotifier.py.desktop")

    #LOG
    #####
    log_dir = stuff_dir + unicode("var/log/")
    #INFO LEVEL FOR DEFAULT
    LOG_LEVEL = 'INFO'
    LOG_FORMATTING = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    #xdg-open FOR DEFAULT
    ######################
    #BROWSER = 'xdg-open'
    BROWSER = 'chromium-browser'
    EDITOR = 'xdg-open'

    #CONFIGURATION
    ###############
    config = MyConfigParser(conf_path)
    REFRESH_TIME = int(config.read_field("time", "refresh"))
    T1 = int(config.read_field("time", "main"))
    T2 = int(config.read_field("time", "message"))

    #ENABLE/DISABLE NOTIFICATIONS
    ##############################
    NOTIFICATIONS = True

    #ABOUT BOX
    #####################################
    ABOUT_ICON = app_home+'data/images/clandiw.png'
    LICENSE = APP_NAME + """ is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public Licence as published
by the Free Software Foundation; either version 3 of the Licence,
or (at your option) any later version.

""" + APP_NAME + """ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
    DESCRIPTION = APP_NAME + """ - A featureful web crawler\nfor http://clandiw.it site"""
    WEBSITE = 'http://tinyurl.com/diwnotifier'
    COPYRIGHT = '(C) 2013 - 2014 Marco Vespo'
    DEVELOPER = 'Marco Vespo <am0n@clandiw.it>'
    ARTIST = 'The DIW crew <http://clandiw.it>'
