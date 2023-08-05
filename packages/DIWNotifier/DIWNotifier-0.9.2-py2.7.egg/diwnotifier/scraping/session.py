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
from urllib2 import URLError, HTTPError
import time
import random
import sys
import logging
module_logger = logging.getLogger('diwnotifier.DIWNotifier.scraping.session')
from settings import Settings


class Page(object):
    def __init__(self, url, page):
        self.url = url
        self.page = page


class Session(object):
    def __init__(self):

        self.import_check()

        self.our_user_agent = ['Mozilla/4.0 (compatible; MSIE 5.0; SunOS 5.10 sun4u; X11)',
                               '''Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.2pre)
                               Gecko/20100207 Ubuntu/9.04 (jaunty) Namoroka/3.6.2pre''',
                               'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser;',
                               'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)',
                               'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1)',
                               'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6)',
                               'Microsoft Internet Explorer/4.0b1 (Windows 95)',
                               'Opera/8.00 (Windows NT 5.1; U; en)',
                               'amaya/9.51 libwww/5.4.0',
                               'Mozilla/4.0 (compatible; MSIE 5.0; AOL 4.0; Windows 95; c_athome)',
                               'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                               'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                               '''Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0;
                               ZoomSpider.net bot; .NET CLR 1.1.4322)''',
                               'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; QihooBot 1.0 qihoobot@qihoo.net)',
                               'Mozilla/4.0 (compatible; MSIE 5.0; Windows ME) Opera 5.11 [en]'
                               ]
        self.br = mechanize.Browser()
        self.login_debug_mode = False
        self.login_status = ''
        self.logger = logging.getLogger('diwnotifier.DIWNotifier.scraping.session.Session')
        self.logger.debug('creating an instance of diwnotifier.DIWNotifier.scraping.session.Session')

    @staticmethod
    def import_check():
        try:
            global mechanize
            import mechanize
        except ImportError:
            mechanize = None
            module_logger.error('Please install mechanize python module first, sudo apt-get install python-mechanize')
            raise ImportError('Please install mechanize python module first, sudo apt-get install python-mechanize')

        try:
            global cookielib
            import cookielib
        except ImportError:
            cookielib = None
            module_logger.error('Please install cookielib python module first')
            raise ImportError('Please install cookielib python module first')

    def login(self, login_url, user, password):
        return self.__loop(self.__login, login_url, user, password)

    def __login(self, login_url, user, password):
        try:
            cj = cookielib.LWPCookieJar()
            self.br.set_cookiejar(cj)

            self.br.set_handle_equiv(True)
            self.br.set_handle_gzip(True)
            self.br.set_handle_redirect(True)
            self.br.set_handle_referer(True)
            self.br.set_handle_robots(False)

            self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
            self.br.add_headers = [('User-agent', random.choice(self.our_user_agent))]

            if Settings.LOG_LEVEL is 'DEBUG':
                self.br.set_debug_http(self.login_debug_mode)
                self.br.set_debug_redirects(self.login_debug_mode)
                self.br.set_debug_responses(self.login_debug_mode)
            #clandiw.it form login
            #####################################
            self.br.open(login_url)
            self.br.select_form(nr=3)
            self.br['ips_username'] = user
            self.br['ips_password'] = password
            req = self.br.click(type='submit', nr=0)
            self.br.open(req)

            response = self.br.response().read()

            resp1 = response.find(
                '<p class=\'message error\'>\n\tNome utente o password non corretti.\n</p>'
            )
            resp2 = response.find(
                '<p class=\'message error\'>\n\tIl tuo account sar&agrave; automaticamente sbloccato fra'
            )

            if resp1 != -1:
                self.login_status = response[resp1+25:(resp1+25)+38].strip()
                return False
            if resp2 != -1:
                self.login_status = response[resp2+25:(resp2+25)+68].strip().replace("&agrave;", "a'")
                return False

        except HTTPError, e:
            self.logger.error('The server couldn\'t fulfill the request...')
            self.logger.error('\tError code: ' + str(e.code))
            sys.exit(1)
        except URLError, e:
            self.logger.warn('We failed to reach a server...')
            self.logger.warn('Reason: ' + str(e.reason))
            #icona offline
            return -1
        except mechanize._mechanize.FormNotFoundError:
            self.logger.error('clandiw.it changing their login system, please report bug at am0n@clandiw.it')
            sys.exit(1)
        else:
            self.login_status = "ok"
            return self.br

    def get_page(self, url):
        return self.__loop(self.__get_page, url)

    def __get_page(self, url):
        try:
            self.br.open(url)
        except URLError, e:
            self.logger.warn('We failed to reach a server...')
            self.logger.warn('Reason: ' + str(e.reason))

            return -1
        else:
            return Page(url, self.br.response().read())

    def __loop(self, function, *args):
        flag = False
        while 1:
            ret = function(*args)
            if ret == -1:
                self.logger.warn('Sleep 3 minutes...')
                time.sleep(180)
                self.logger.warn('Try again...')
                flag = True
            else:
                if flag:
                    self.logger.warn('ok')
                return ret
