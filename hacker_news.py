#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json
import urllib2
import time
import libnotif
from pprint import pprint

stream_title = 'http://apify.heroku.com/api/hacker_news.json'


notification_stream = libnotif.NotifConn('localhost', 50012)
notification_stream.connect()

notification_stream.send_notif('Hacker News submission stream connected')

local_compare = True
first_time = False

cached_data = []

if local_compare:
    fh = open('test_data.json', 'r')
    cached_data.append(json.loads(fh.read()))
    fh.close()


def get_value(dictionary, field):
    to_output = []
    for submission in dictionary:
        to_output.append(str(submission[field].encode('ascii', 'replace')))
    return to_output


def multi_in(what, in_what):
    for item in map(str, in_what):
        item = str(item.encode('ascii', 'replace'))
        if what in item:
            return True
    # print 'heh'
    return False


while True:
    print 'fetching data... ',
    raw_data = urllib2.urlopen(stream_title).read()
    data = json.loads(raw_data)
    # if not local_compare:
    cached_data.append(data)
    if not first_time:
        print 'retrieved...',

    new_data = []
    # now we are going to check if there is anything new in the stream :D

    if not first_time:
        previous_titles = get_value(cached_data[-2], "title")
        for submission in data:
                if not multi_in(
                    str(submission["title"].encode('ascii', 'replace')),
                    map(str, previous_titles)):
                        new_data.append(submission)

        if len(new_data) != 0:
            print 'new submissions;', len(new_data)
            notification_stream.send_notif('New submissions; ' + str(len(new_data)))
            pprint(get_value(new_data, "title"))
        else:
            print 'no new posts', len(new_data)
        # break
    else:
        print 'cached', len(cached_data)
        first_time = False

    time.sleep(30)


notification_stream.disconnect()
