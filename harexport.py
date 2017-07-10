#!/usr/bin/env python

'''
Chrome generated HAR file parser. Can be used via CLI:

harexport.py file.har > file.csv
'''

import sys
import json
import csv
import StringIO

def parseharline(line):
    '''Receives and entry from a HAR file and returns a summary with relevant data.'''
    r={}
    for t in line['timings']:
        if line['timings'][t]==-1:
            line['timings'][t]=0
    r['transfertime']=line['timings']['send']+line['timings']['receive']
    r['servertime']=sum(line['timings'].values())-r['transfertime']
    r['reqcookies']=bool(line['request']['cookies'])
    headers=dict([(i['name'].lower(),i['value']) for i in line['response']['headers']])
    for h in ('expires','cache-control','etag','last-modified','content-encoding'):
        r[h.lower().replace('-','')]=headers.get(h,'')
    r['size']=line['response']['content']['size']
    r['transfersize']=line['response']['_transferSize']
    r['contenttype']=line['response']['content']['mimeType']
    r['url']=line['request']['url']
    r['protocol']=line['response']['httpVersion']
    return r

def parsehar(filename):
    '''Opens and parses a HAR file'''
    hartext=open(filename).read()
    hardata=json.loads(hartext)
    return hardata['log']['pages'][0]['pageTimings'],map(parseharline,hardata['log']['entries'])

def buildcsv(headers,values):
    '''Receives a list of headers and a list of lists of values and returns plain CSV text.'''
    lines=[headers[:]]
    for v in values:
        line=[]
        for h in headers:
            line.append(v[h])
        lines.append(line)
    sfile=StringIO.StringIO()
    writer=csv.writer(sfile)
    writer.writerows(lines)
    sfile.seek(0)
    return sfile.read()

def main():
    '''CLI'''
    if len(sys.argv)<2:
        print 'Usage:\n%s file.har' % sys.argv[0]
        sys.exit(1)
    data=parsehar(sys.argv[1])
    headers=["url", "contenttype", "transfersize", "size", "contentencoding", "protocol", "servertime", "transfertime", "reqcookies", "expires", "lastmodified", "etag", "cachecontrol"]
    csv=buildcsv(headers,data[1])
    print csv

if __name__ == '__main__':
    main()

