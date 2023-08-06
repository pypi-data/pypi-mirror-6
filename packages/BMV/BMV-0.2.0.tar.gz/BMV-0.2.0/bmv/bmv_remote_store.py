#
# Filename: bmv_remote_store.py
# Licence: https://raw.githubusercontent.com/jepefe/bmvmonitor/master/LICENSE

import httplib
import urllib2
import urllib
from urlparse import urlparse
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json

class BMVRemoteStore(object):
    """An interface to store BMV data to a web server"""

    @staticmethod
    def getDeviceStatus(token, date_time, bmv_data):
        """prepare the URL params

        Keyword arguments:

        token     -- The token for the web service
        date_time -- If provided, attach a datetime to the URL params
        bmv_data  -- The data to store
        """

        devices_status = "device="+json.dumps(bmv_data)

        if token:
            devices_status = devices_status+"&token="+ token

        if date_time:
            devices_status = devices_status+"&datetime="+str(datetime.now())

        return devices_status


    @staticmethod
    def store(url, date_time, token, bmv_data):
        """Stores BMV data into the web server

        Keyword arguments:

        url       -- The URL to report to
        date_time -- If provided, attach a datetime to the URL params
        token     -- The token for the web service
        bmv_date  -- The data to store
        """

        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }

        urllist = urlparse(url)

        if urllist.scheme != 'http':
            print "Invalid URL, by example http://somewere.com/page.php"
            return
        else:

            try:

                conn = httplib.HTTPConnection( urllist.netloc )
                
                devices_status = BMVRemoteStore.getDeviceStatus(token, date_time, bmv_data)

                conn.request("POST", urllist.path, devices_status , headers)
                response = conn.getresponse()

            except:
                print 'Network error, retrying'

if __name__ == '__main__':
    help(BMVRemoteStore)

"""

Documentation

- https://docs.python.org/2/library/urlparse.html

"""
