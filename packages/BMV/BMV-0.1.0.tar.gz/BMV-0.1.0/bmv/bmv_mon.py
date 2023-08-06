#!/usr/bin/python
# Filename: bmv_mon.py

#Copyright (C) 2014 Jesus Perez <jepefe@gmail.com>
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License at <http://www.gnu.org/licenses/>
#for more details.

from bmv               import bmv
from bmv_remote_store  import BMVRemoteStore
from bmv_local_factory import Formats, BMVLocalFactory

import time
import os
from optparse import OptionParser

try:
    import json
except ImportError:
    import simplejson as json




def main():
    parser = OptionParser()

    #Documentation options
    parser.add_option('-d','--doc', help='Display pydoc', action='store_true', dest='doc')

    #General options
    parser.add_option('-p','--port',help='Port to listen',dest='port')
    parser.add_option('-m','--model',help='Use this option if your device is a BMV602 model.',dest='model', action='store_true',default=False)
    parser.add_option('-c','--continuous',help='Print data continuously',dest="continuous",action='store_true',default=False)
    parser.add_option('-i','--interval',help='Time interval between reads in seconds. Use with -c',dest='time_interval',default=0)


    parser.add_option('-j','--json',help='Prints json formatted string with all devices status to stdout',dest='json',\
                      default=False,action='store_true')

    #URL reporting options
    parser.add_option('-n','--datetime',help='Include date and time and send to url. Use with -u.',dest="date_time",action='store_true',default=False)
    parser.add_option('-u','--send-json-url',help='Send json via POST to specified url',dest='url')
    parser.add_option('-t','--token',help='Include security token and send to url. Use with -u.',dest='token')

    #File reporting options
    parser.add_option('-f', '--file',   help="Store data into specified file (defaul format csv)",       dest="file")
    parser.add_option('', '--format', help="Save data in a specific format [csv,sqlite]. Use with -f", dest='format')

    (options, args) = parser.parse_args()

    if options.doc:
        help(bmv)
    else:
        start(options)


def start(options):

    if options.port:
        if options.model:
            bmvd = bmv(options.port,602)
        else:
            bmvd = bmv(options.port,600)
    else:
        print "Port is mandatory"
        return

    #Set continuous to true for first iteration
    continuous = True

    while continuous:

        #Set continuous mode if selected
        continuous = options.continuous

        try:
            bmv_data= bmvd.get_data()
        except:
            print "Error retreiving data, retrying"

        #Send json to url
        if options.url:

            BMVRemoteStore.store(
                options.url,
                options.date_time,
                options.token,
                bmv_data
            )

        elif options.file:

            BMVLocalFactory.factory(
                options.format,
                options.file, 
                bmv_data
            )

        #Clear screen
        #os.system('cls' if os.name == 'nt' else 'clear')

        #Print status in json format
        if options.json:
            os.system('cls' if os.name == 'nt' else 'clear')
            print json.dumps(bmv_data)
        

        #Set interval
        if options.time_interval > 0:
            for i in range(1,int(options.time_interval)):
                time.sleep(1)


if __name__ == '__main__':
    main()
