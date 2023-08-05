"""
	Developed by 
	Andrea Stagi <stagi.andrea@gmail.com>

	Tiny4py: python wrapper to use main url shortener services in your apps
	Copyright (C) 2010 Andrea Stagi

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Lesser General Public License as published 
	by the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Lesser General Public License for more details.

	You should have received a copy of the GNU Lesser General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from shorteners.tinyurl_shortener import TinyurlShortener
from shorteners.google_shortener import GoogleShortener
from shorteners.bitly_shortener import BitlyShortener
from shorteners.shortener import *


def getShortener(ids):
    shrt = Shortener()

    if ids == GOOGLE_ID:
        shrt = GoogleShortener()

    elif ids == BITLY_ID:
        shrt = BitlyShortener()

    elif ids == TINYURL_ID:
        shrt = TinyurlShortener()

    return shrt

