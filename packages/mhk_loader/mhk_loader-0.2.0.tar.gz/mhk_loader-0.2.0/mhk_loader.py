#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013,2014 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Maheki loader

Tsung scenario must be configured with loglevel="notice"

<tsung loglevel="notice" dumptraffic="false" version="1.0">

"""
import sys
import os
import re
import urllib
import requests
from optparse import OptionParser
import json
from socket import socket
from time import sleep


__version__ = "0.2.0"


def arg_parse():
    """ Parse command line arguments """
    arg_list = "-i FILENAME -u USER -k APIKEY -s SERVER [-vh]"
    usage = "Usage: %prog " + arg_list
    parser = OptionParser(usage, version=__version__)

    port = 80
    if os.getenv('MAHEKI_PORT') is not None:
        port = os.getenv('MAHEKI_PORT')

    protocol = 'http'
    if os.getenv('MAHEKI_PROTOCOL') is not None:
        protocol = os.getenv('MAHEKI_PROTOCOL')


    parser.add_option("-a", "--api", dest="api",
                      help="api path",
                      default="/api/v1/")
    parser.add_option("-i", "--infile", dest="infile",
                      help="input file",
                      default=None)
    parser.add_option("-u", "--user", dest="user",
                      help="api username",
                      default=os.getenv('MAHEKI_USER'))
    parser.add_option("-k", "--key", dest="key",
                      help="api key",
                      default=os.getenv('MAHEKI_APIKEY'))
    parser.add_option("-s", "--server", dest="hostname",
                      help="maheki hostname",
                      default=os.getenv('MAHEKI_HOST'))
    parser.add_option("-r", "--run", dest="run",
                      help="run id",
                      default=None)
    parser.add_option("-b", "--bench", dest="bench",
                      help="bench id",
                      default=None)
    parser.add_option("-p", "--port", dest="port",
                      help="maheki port",
                      default=port)
    parser.add_option("--protocol", dest="protocol",
                      help="protocol http / https, default: http",
                      default=protocol)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true",
                      help="be verbose",
                      default=False)

    return parser.parse_args()[0]


def check_options(options):
    """Check mandatory options"""
    if options.infile is None:
        print """Input file is required, use -i on command line"""
        sys.exit(1)

    if options.run and options.bench is None:
        print """Run id is mandatory, use -r on command line"""
        sys.exit(1)


def parse_file(fpath):
    """
    Parse the content of tsung.log file

    Parameters:
     - fpath (string): filepath containing tsung log

    Return a json object
    """
    print "Parse file : {}\n".format(fpath)
    starg = "ts_client:\((\d+:<\d+.\d+.\d+>)\) Starting new transaction (\w+) \(now{(\d+),(\d+),(\d+)}\)"
    stprg = "ts_client:\((\d+:<\d+.\d+.\d+>)\) Stopping transaction (\w+) \({(\d+),(\d+),(\d+)}\)"
    starts = []
    stops = []
    f = open(fpath, 'r')
    i = -1
    j = -1
    for line in f:
        if i == 1:
            alpha = alpha + line.strip()

            rgx = re.compile(starg)
            match = rgx.search(alpha)
            transac = match.group(2)
            time = "{}{}".format(match.group(3), match.group(4))
            micro = "{}".format(match.group(5))
            key = match.group(1)

            #print "{} {} \n".format(transac, time)
            starts.append({"tr": transac, "start": time, "micro": micro, "client": key})
            i = -1
        if j == 1:
            stop = stop + line.strip()
            #print stop
            rgs = re.compile(stprg)
            match = rgs.search(stop)
            transac = match.group(2)
            time = "{}{}".format(match.group(3),
                                    match.group(4))
            micro = "{}".format(match.group(5))

            key = match.group(1)

            #print "{} {} \n".format(transac, time)
            stops.append({"tr": transac, "stop": time, "micro": micro, "client": key})
            j = -1
        if j == 0:
            stop = stop + line.strip()
            j = j + 1
        if i == 0:
            alpha = alpha + line.strip()
            i = i + 1
        if 'Starting new transaction' in line:
            alpha = line.strip()
            i = 0
        if 'Stopping transaction' in line:
            stop = line.strip()
            j = 0

    return starts, stops

def upload_api(value):
    """Format datas for tastypie
    """
    data = {"value": value['value'],
            "datetms": value['datetms'],
            "name": value['name'],
            "run": "/api/v1/run/{}/".format(value['run'])}

    return data

def post(mdata, auth, address):
    """
    Call Maheki API
    """

    data = json.dumps(upload_api(mdata))

    parms = {'username': auth['username'],
             'api_key': auth['key']}

    url = '{}pom/?{}'.format(address, urllib.urlencode(parms))
    response = requests.post(url,
                             data=data,
                             headers={'content-type': 'application/json'})

    if response.status_code == 201:
        sys.stdout.write(".")
        sys.stdout.flush()
    else:
        print response.status_code, url, data
        sys.exit(1)

def api_get(address, auth, ressource, rid):
    """
    Call Maheki API
    """
    parms = {'username': auth['username'],
             'api_key': auth['key']}

    url = '{}{}/{}/?{}'.format(address,
                               ressource,
                               rid,
                               urllib.urlencode(parms))

    response = requests.get(url,
                            headers={'content-type': 'application/json'})

    if response.status_code == 200:
        return response.content
    else:
        print "Error on run"
        print response.status_code, url
        sys.exit(1)



def process(fpath, auth, url, run):
    """Process a file
    """
    if fpath is not None:
        if not os.path.exists(fpath):
            sys.exit(1)
        else:
            # parse file and return nodes
            starts, stops = parse_file(fpath)


    if len(starts) > 0:
        print len(starts), len(stops)
        while (len(starts)):
            start = starts.pop(0)
            i = -1
            for stopi in stops:
                i = i + 1
                if (stopi['client'] == start['client'] and stopi['tr'] == start['tr']):
                    stop = stops.pop(i)
                    delta = (float(stop['stop']) - float(start['start'])) * 1000000
                    delta = delta + float(stop['micro']) - float(start['micro'])
                    value = {"name": start['tr'],
                             "value": delta / 1000,
                             "datetms": stop['stop'],
                             "run": run}
                    post(value, auth, url)
                    break
    sys.stdout.write("\n")
    sys.stdout.flush()


def build_auth(options):

    auth = {'username': options.user, 'key': options.key}
    return auth


def check_run(run):
    """Check is the returned run is valid
    """
    try:
        data = json.loads(run)
    except:
        sys.exit()

    if 'id' in data:
        return 0
    else:
        print "Invalid run"
        sys.exit()


def newrun(bench, code, address, auth):
    """
    rodo@elz:~$ curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"start": "2013-04-02 18:40", "stop": "2013-04-0219:40", "bench": "/api/v1/bench/1/" }' http://127.0.0.1:8000/api/v1/run/
    """
    rid = None

    data = {"start": "2013-04-02 18:40",
            "stop": "2013-04-02 19:40",
            "code": code,
            "bench": "/api/v1/bench/{}/".format(bench)}

    parms = {'username': auth['username'],
             'api_key': auth['key']}

    url = '{}run/?{}'.format(address, urllib.urlencode(parms))

    response = requests.post(url,
                             data=json.dumps(data),
                             headers={'content-type': 'application/json'})

    if response.status_code == 201:
        loc = response.headers['location']
        rid = loc.split('/')[-2]
        sys.stdout.write(".")
        sys.stdout.flush()
    else:
        print "Can't create run, error {}".format(response.status_code)
        sys.exit(1)

    return rid

def getfilenames(dpath):
    """Return the code and filenames from directory name
    """
    if not dpath.endswith('/'):
        dpath = "{}/".format(dpath)

    if os.path.isdir(dpath):
        code = os.path.basename(os.path.dirname(dpath))
        allfiles = os.listdir(dpath)
        return code, logfiles(allfiles, dpath)
    else:
        print "Error infile is not a directory"
        sys.exit(1)

def logfiles(files, dpath):
    """
    Return logfiles in an array of filenames
    """
    result = []
    pattern = "tsung\d+.*\.log$"
    rgx = re.compile(pattern)
    for fname in files:
        if re.match(rgx, fname):
            result.append(os.path.join(dpath, fname))
    return result

def main():
    """Main programm"""
    options = arg_parse()
    check_options(options)
    auth = build_auth(options)

    address = "{}://{}:{}{}".format(options.protocol,
                                    options.hostname,
                                    options.port,
                                    options.api)

    run_code, files = getfilenames(options.infile)

    run_id = newrun(options.bench, run_code, address, auth)

    if run_id:
        run = api_get(address, auth, "run", run_id)

        check_run(run)

        for fpath in files:
            process(fpath, auth, address, run_id)



if __name__ == '__main__':
    main()
