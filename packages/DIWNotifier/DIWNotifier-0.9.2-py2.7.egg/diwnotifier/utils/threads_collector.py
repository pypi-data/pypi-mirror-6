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
import threading


class ThreadsCollector(object):

    def __init__(self, *jobs):
        self.jobs = jobs
        self.threads = []

    def make(self):
        for job in self.jobs:
            thread = threading.Thread(target=job)
            self.threads.append(thread)

    def start_all(self):
        for thread in self.threads:
            thread.start()

    def join_all(self):
        for thread in self.threads:
            thread.join()

    def clean_all(self):
        del self.threads[:]
