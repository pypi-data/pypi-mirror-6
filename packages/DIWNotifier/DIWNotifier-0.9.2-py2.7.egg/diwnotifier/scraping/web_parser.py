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
import copy
import sys
from session import Page
from utils import download_avatar
import logging
module_logger = logging.getLogger('diwnotifier.DIWNotifier.scraping.web_parser')


class WebParser(object):
    def __init__(self):
        self.import_check()
        self.message = 'clandiw.it changing their system, please report bug at am0n@clandiw.it'
        self.pages = []
        self.notification_data = {}
        self.msg_data = {}
        self.quote_string = ""
        self.friends_online = {}
        self.new_content = []
        self.last_shout = {'what': '', 'who': '', 'when': '', 'avatar': ''}
        self.logger = logging.getLogger('diwnotifier.DIWNotifier.scraping.web_parser.WebParser')
        self.logger.debug('creating an instance of diwnotifier.DIWNotifier.scraping.web_parser.WebParser')

    @staticmethod
    def import_check():
        try:
            global BeautifulSoup
            from BeautifulSoup import BeautifulSoup
        except ImportError:
            BeautifulSoup = None
            msg = 'Please install beautifulsoup python module first, sudo apt-get install python-beautifulsoup'
            module_logger.error(msg)
            raise ImportError(msg)

    def add_page(self, p):
        if type(p) == Page:
            self.pages.append(p)
            return p.page
        return False

    def clean_pages(self):
        del self.pages[:]

    def search_page(self, url):
        for p in self.pages:
            if p.url is url:
                return p.page
        return "-1"

    #ALL
    def get_notification_count(self, string):
        page = self.pages[0].page
        if not page is '-1':
            try:
                if page.find(string) == -1:
                    return "0"
                anchor = page.index(string)
                sub = page[anchor + len(string):anchor + len(string) + 2]
                if sub[1] == "<" or sub[1] == " ":
                    count = sub[0]
                else:
                    count = sub[0:2]
            except ValueError:
                self.logger.error(self.message)
                sys.exit(1)
            else:
                return count
        else:
            return False

    #PAGE=MSG_URL
    def get_unread_msgs_count(self):
        page = self.search_page(Settings.MSG_URL)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                count = soup.find('li', attrs={'id': 'f_new'}).span.text.strip()
            except ValueError:
                self.logger.error(self.message)
                sys.exit(1)
            else:
                return str(count)
        else:
            return False

    #PAGE=NOTIFICATIONS_URL
    def get_last_notification(self):
        page = self.search_page(Settings.NOTIFICATIONS_URL)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                self.notification_data['avatar'] = download_avatar(
                    soup.find('td', attrs={'class': 'col_n_photo short'}).img['src'], Settings.avatars_path)
                self.notification_data['what'] = str(soup.find('h4')).rstrip('</h4>').lstrip('<h4>').strip()
                self.notification_data['who'] = soup.find('h4').a["href"]
                self.notification_data['when'] = soup.find('td', attrs={'class': 'col_n_date desc'}).a.string

            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return self.notification_data
        else:
            return False

    #PAGE=MSG_URL
    def get_last_msg_detail(self):
        page = self.search_page(Settings.MSG_URL)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                self.msg_data['avatar'] = unicode(
                    download_avatar(
                        soup.find('td',
                                  attrs={'class': 'col_f_post'}).a.img['src'],
                        Settings.avatars_path
                    )
                )
                self.msg_data['what_link'] = unicode(
                    soup.find('a', attrs={'title': 'Visualizza questa conversazione'})['href']
                )
                self.msg_data['what'] = unicode(
                    soup.find('a', attrs={'title': 'Visualizza questa conversazione'}).string.strip()
                )
                self.msg_data['who_link'] = unicode(
                    soup.find('ul', attrs={'class': 'last_post ipsType_small'}).li.a['href']
                )
                self.msg_data['who'] = unicode(
                    soup.find('ul', attrs={'class': 'last_post ipsType_small'}).li.a.span.text
                )
                self.msg_data['when'] = unicode(soup.find('li', attrs={'class': 'desc'}).a.string)

            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return self.msg_data
        else:
            return False

    #PAGE=MSG_URL
    def get_quote_string(self):
        page = self.search_page(Settings.MSG_URL)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                self.quote_string = str(
                    soup.find('div', attrs={'id': 'space_allowance'}).find('span', attrs={'class': 'desc'})
                ).lstrip('<span class="desc">')
                self.quote_string = self.quote_string.rstrip('</span>')
            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return self.quote_string
        else:
            return False

    #ALL
    def get_main_avatar(self):
        page = self.pages[0].page
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                link = soup.find('img', attrs={'class': 'user_photo'})['src']
            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return link
        else:
            return False

    #PAGE=FRIENDS_URL
    def get_friends_online(self, friendsc):
        page = self.search_page(Settings.FRIENDS_URL)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                i = 0
                for h3 in soup.findAll('h3', attrs={'class': 'ipsType_subtitle'}):
                    if i < int(friendsc):
                        if not h3.a.span.string is None:
                            self.friends_online[h3.a.span.string] = h3.a['href']
                        else:
                            self.friends_online[h3.a.span.span.string] = h3.a['href']
                        i += 1
                    else:
                        break

            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return self.friends_online
        else:
            return False

    #PAGE=NEW_CONTENT
    def get_new_content(self):
        page = self.search_page(Settings.NEW_CONTENT)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)

                if len(self.new_content) > 0:
                    del self.new_content[0:len(self.new_content)]

                for a in soup.findAll('a', attrs={'title': 'Visualizza risultato'}):
                    self.new_content.append(Topic(a.string, a['href']+"?view=getnewpost"))
                i = 0
                for img in soup.findAll('img', attrs={'alt': 'Hai scritto in questa discussione'}):
                    self.new_content[i].set_read(img['src'])
                    i += 1

            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return self.new_content
        else:
            return False

    def get_link(self, url, title):
        page = self.search_page(url)
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                a = soup.find('a', attrs={'title': title})
            except ValueError:
                print self.message
                sys.exit(1)
            else:
                if not a is None:
                    return a['href']
                else:
                    return False
        else:
            return False

    #ALL
    def get_last_shout(self):
        page = self.pages[0].page
        if not page is '-1':
            try:
                soup = BeautifulSoup(page)
                first_row = soup.find('table', attrs={'id': 'shoutbox-shouts-table'}).tbody.tr
                i = 0
                for td in first_row.findAll('td', recursive=False):
                    if i is 0:
                        self.last_shout['avatar'] = unicode(download_avatar(td.img['src'], Settings.avatars_path))
                    if i is 1:
                        self.last_shout['who'] = td.findAll('a', recursive=False)[1].span.span.string
                    if i is 3:
                        span = td.find('span', attrs={'class': 'right desc'})
                        self.last_shout['when'] = span.findAll(text=True)[0].rstrip(' )&nbsp;')+")"
                        self.last_shout['what'] = td.find('span', attrs={'class': 'shoutbox_text'}).text
                    i += 1
            except ValueError:
                print self.message
                sys.exit(1)
            else:
                return copy.deepcopy(self.last_shout)
        else:
            return False


class Topic(object):
    def __init__(self, title, link):
        self.title = title
        self.link = link

        self.dot_uri = ''

        self.tags = []
        self.section = ''

        self.replies = -1
        self.last_replies = ''
        self.last_replies_from = ''

        self.visits = -1
        self.started = ''
        self.started_by = ''

    def set_read(self, dot_url):
        if 'unread' in dot_url:
            self.dot_uri = 'data/images/icons/t_unread_dot.png'
        else:
            self.dot_uri = 'data/images/icons/t_read_dot.png'

    def get_unread_link(self):
        return self.link+"?view=getnewpost"
