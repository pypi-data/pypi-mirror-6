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
import sys
import os

import logging
logging.basicConfig()
module_logger = logging.getLogger('utils.utils')
module_logger.setLevel("INFO")
#module_logger.setLevel("DEBUG")
import threading


class Thread(threading.Thread):
    def __init__(self, t, *args):
        self.handled = False
        threading.Thread.__init__(self, target=t, args=args)
        self.setDaemon(True)
        self.start()

#CONFIG PARSER
###############
import ConfigParser


class MyConfigParser(object):
    def __init__(self, path):
        self.config = ConfigParser.RawConfigParser()
        self.path = path
        self.report_bug_at = 'foo@bar.com'

        self.logger = logging.getLogger('utils.utils.MyconfigParser')
        self.logger.debug('creating an instance of utils.utils.MyconfigParser')

    def read_field(self, section, field):
        try:
            self.config.read(self.path)
            field_value = self.config.get(section, field)
        except ConfigParser.Error:
            module_logger.error('Error reading config file ' + self.path + ', please report bug at '+self.report_bug_at)
            sys.exit(1)
        else:
            return field_value

import subprocess


def download_avatar(link, uri):
    flag = False
    if link.find("gravatar.com") != -1 and not link.find('default_large.png'):
        waldo = link.split("/")
        waldo = waldo[4].split("&")
        waldo = waldo[0]
        flag = True
    elif link.find("clandiw.it/uploads/") != -1:
        waldo = link.split("/")
        waldo = waldo[5]
        flag = True
    else:
        waldo = "default_large.png"
    if flag:
        if not os.path.exists(uri + "" + waldo):
            p = subprocess.Popen(['wget', '-P', uri, link])
            p.communicate()
    return uri + "" + waldo


def bool_print(string, function, *args):
    if hasattr(function, '__call__'):
        flag = True if function(*args) else False
    else:
        flag = True if function else False

    module_logger.info(string) if flag else module_logger.error(string)

    return flag


def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, w=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n', 1)[0]) >= w)],
                   word),
                  text.split(' '))

import re


def get_desktop_environment():
        #From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=1139057
        if sys.platform in ["win32", "cygwin"]:
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else: #Most likely either a POSIX system or something not much common
            desktop_session = os.environ.get("DESKTOP_SESSION")
            if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                       "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                    return desktop_session
                ## Special cases ##
                # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
                # There is no guarantee that they will not do the same with the other desktop environments.
                elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                    return "xfce4"
                elif desktop_session.startswith("ubuntu"):
                    return "unity"
                elif desktop_session.startswith("lubuntu"):
                    return "lxde"
                elif desktop_session.startswith("kubuntu"):
                    return "kde"
                elif desktop_session.startswith("razor"): # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                    return "windowmaker"
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                return "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                    return "gnome2"
            #From http://ubuntuforums.org/showthread.php?t=652320
            elif is_running("openbox"):
                return "openbox"
            elif is_running("xfce-mcs-manage"):
                return "xfce4"
            elif is_running("ksmserver"):
                return "kde"
        return "unknown"


def is_running(process):
        #From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
        # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
        try: #Linux/Unix
            s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
        except: #Windows
            s = subprocess.Popen(["tasklist", "/v"],stdout=subprocess.PIPE)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False


def check_notification_daemon():
    daemons = ["dunst", "notify-osd", "xfce4-notifyd", "plasma-widgets-workspace", "notification-daemon"]
    for daemon in daemons:
        if is_running(daemon):
            return daemon

    return False


#https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None