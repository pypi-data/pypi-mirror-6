"""
	Developed by 
	Andrea Stagi <stagi.andrea@gmail.com>

	Tiny4py: python wrapper to use main url shortener services in your apps
	Copyright (C) 2010 Andrea Stagi

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

try:
    from re import match
    from urllib2 import urlopen, Request, HTTPError, URLError
    from urllib import quote, urlencode
    import urllib
    from simplejson import loads

except ImportError, e:
    raise Exception('Required module missing: %s' % e.args[0])

from shortener_error import *
from consts import *
from qrcode import *


class Shortener(QrCode):
    def __init__(self):
        QrCode.__init__(self)

    def _formatUrl(self, url):
        if not (url[0:7] == "http://"):
            url = "http://" + url
        return url

    def getLongurl(self, url):

        try:
            f = urllib.urlopen(url)
            return f.geturl()
        except URLError, e:
            raise ShortenerError("Connection error: %s" % e)
        except IOError, err:
            raise ShortenerError("Connection error: %s" % err)

    def _genericRequestMethod(self, url, function, params={}, callback=None):

        url = Shortener._formatUrl(self, url)

        try:
            if callback == None:
                return function(url, params)
            else:
                callback(function(url, params))

        except URLError, e:
            raise ShortenerError("Connection error: %s" % e)
        except HTTPError, hte:
            raise ShortenerError("Http error: %s" % hte)
        except IOError:
            raise ShortenerError("Name or service not known")

    def getShorturl(self, url, params={}, callback=None):
        return self._genericRequestMethod(url, self._shortRequest, params, callback)

    def setApi(self, user, apikey):
        return None

    def _getBaseUrl():
        raise NotImplementedError

    def _getBaseUrlParameters():
        raise NotImplementedError

    def _shortRequest(self, url):
        raise NotImplementedError

    def _genericRequest(self, baseurl, params, method="POST"):

        if (method == "POST"):
            req = Request(self._getBaseUrl() + baseurl, urlencode(params))
        else:
            req = Request(self._getBaseUrl() + baseurl + "?" + urlencode(params))

        response = urlopen(req)
        return response.read()

    def _getBaseUrl():
        return self.__baseurl

    def _setBaseUrlParameters(self, params={}):
        self.__baseurlparameters = params

    def _getBaseUrlParameters(self, params={}):
        self.__baseurlparameters.update(params)
        return self.__baseurlparameters
		

