#!/usr/bin/env python

import datetime
import time
from utils import urlLinks
import re
import urllib2

baseURL = 'http://inbound-archive.pub.build.mozilla.org/pub/mozilla.org/firefox/tinderbox-builds/mozilla-inbound-linux/'

timestamps = map(lambda l: int(l.get('href').strip('/')), urlLinks(baseURL))
start = (datetime.datetime(2013, 11, 6), '70de5e24d79b')
end = (datetime.datetime(2013, 11, 8), '70f21fad60a4')
range = 60*60*4 # anything within four hours is potentially within the range
valid_timestamps = filter(lambda t: t > (time.mktime(start[0].timetuple()) - range) and t < (time.mktime(end[0].timetuple()) + range), timestamps)
for timestamp in valid_timestamps:
    for link in urlLinks("%s%s/" % (baseURL, timestamp)):
        href = link.get('href')
        if re.match('.*txt', href):
            url = "%s%s/%s" % (baseURL, timestamp, href)
            contents = urllib2.urlopen(url).read()
            rev = None
            for line in contents.splitlines():
                parts = line.split('/rev/')
                if len(parts) == 2:
                    rev = parts[1]
                    break
            if rev:
                print (datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'), rev)

