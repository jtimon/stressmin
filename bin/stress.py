# import urllib
# import urllib2

    # if action == 'post':
    #     data = urllib.urlencode(data)
    #     print url, data
    #     req = urllib2.Request(url, data)
    # elif action == 'get':
    #     if data:
    #         url_values = urllib.urlencode(data)
    #         url = url + '?' + url_values
    #     req = urllib2.Request(url)
    # elif action == 'put':
    #     data = urllib.urlencode(data)
    #     req = urllib2.Request(url, data)
    #     req.add_header('Content-Type', 'application/json')
    #     req.get_method = lambda: 'PUT'
    # else:
    #     raise NotImplementedError

    # try:
    #     response = urllib2.urlopen(req)
    #     the_page = response.read()
    #     print ('%s: %s bytes: %r' % (url, len(the_page), the_page[:50]))

    # except urllib2.HTTPError as e:
    #     print e.code
    #     print e.read() 
    # except urllib2.URLError as e:
    #     print e.reason


#!/usr/bin/env python
if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import gflags

gflags.DEFINE_string('url', u"http://localhost:8100",
    u"")

gflags.DEFINE_string('data', u"",
                     u"",
                     short_name='d')

gflags.DEFINE_string('params', u"",
                     u"")

gflags.DEFINE_string('auth', u"", u"")

gflags.DEFINE_bool('repeat', False, '')

gflags.DEFINE_string('action', u"get", u"")
gflags.DEFINE_float('sleeptime', 1.0, u"")

gflags.DEFINE_integer('threads', 1,
    u"Number of threads",
    short_name='t')
gflags.RegisterValidator('threads',
    lambda workers: 1 <= workers <= 2000,
    message=u"Number of threads must be between 1 and 2000.")

gflags.DEFINE_integer('processes', 1,
    u"Number of processes",
    short_name='p')
gflags.RegisterValidator('processes',
    lambda workers: 1 <= workers <= 2000,
    message=u"Number of processes must be between 1 and 2000.")

try:
    import sys
    argv = gflags.FLAGS(sys.argv)
except gflags.FlagsError, e:
    print('%s\n\nUsage %s ARGS \n%s' % (e, sys.argv[0], gflags.FLAGS))
    sys.exit(0)
FLAGS = gflags.FLAGS

# ===----------------------------------------------------------------------===

import gevent
from gevent import monkey

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

import json
import requests

def execute_thread():

    if FLAGS.auth:
        user, password = FLAGS.auth.split(':')
        auth = (user, password)
    else:
        auth = None

    if FLAGS.params:
        params = json.loads(FLAGS.params)
    else:
        params = None

    if FLAGS.action == 'get':
        response = requests.request(FLAGS.action, FLAGS.url, params=params, auth=auth)
    else:
        response = requests.request(FLAGS.action, FLAGS.url, data=FLAGS.data, params=params,
                                    auth=auth, headers = {'content-type': 'application/json'})

    the_page = response.text
    print ('%s: %s bytes: %r' % (FLAGS.url, len(the_page), the_page[:50]))
    response.raise_for_status()
    # import pprint
    # pprint.pprint(response.json())

class Thread(gevent.Greenlet):
    
    def _run(self):
        execute_thread()

import time
import multiprocessing

class Process(multiprocessing.Process):

    def __init__(self, threads, repeat, sleep_time,
                 *args, **kwargs):
 
        self.threads = threads
        self.repeat = repeat
        self.sleep_time = sleep_time

        super(Process, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            """Spawn multiple workers and wait for them to complete"""
            jobs = []
            for thread_id in range(self.threads):
                t = Thread()
                t.start()
                jobs.append(t)
            gevent.joinall(jobs)
            
            if not self.repeat:
                break
            time.sleep(self.sleep_time)

# ===----------------------------------------------------------------------===

# time.sleep(4)

for process_id in range(FLAGS.processes):
    p = Process(FLAGS.threads, FLAGS.repeat, FLAGS.sleeptime)
    p.start()

# time.sleep(10)
