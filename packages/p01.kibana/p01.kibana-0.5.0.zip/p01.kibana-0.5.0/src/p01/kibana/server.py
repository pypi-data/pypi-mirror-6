###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Kibana server
$Id: server.py 3921 2014-01-04 23:07:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"


import cStringIO
import optparse
import os
import signal
import string
import sys
import time
import traceback

import gevent
import gevent.queue
import gevent.socket
from gevent.thread import allocate_lock as Lock

# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break

import p01.kibana.backend


socket = gevent.socket

lock = Lock()

# constants
INTERVAL = 5.0
MAX_PACKET = 2048
MAX_QUEUE_SIZE = 1000
MAX_BATCH_SIZE = 250


def parse_addr(text):
    "Parse a 1- to 3-part address spec."
    if text:
        parts = text.split(':')
        length = len(parts)
        if length== 3:
            return parts[0], parts[1], int(parts[2])
        elif length == 2:
            return None, parts[0], int(parts[1])
        elif length == 1:
            return None, '', int(parts[0])
    return None, None, None


##############################################################################
#
# scheduler

class Scheduler(object):
    """Gevent based function scheduler"""

    def __init__(self, interval, function, *args, **kwargs):
        self.greenlet = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.stopped = False
        self.start()

    def worker(self):
        while True:
            if self.stopped:
                break
            # process and sleep
            gevent.spawn(self.function, *self.args, **self.kwargs)
            gevent.sleep(self.interval)

    def start(self):
        self.greenlet = gevent.spawn(self.worker)

    def stop(self):
        self.stopped = True
        gevent.sleep(self.interval + 1)
        self.greenlet.kill()


##############################################################################
#
# server

class KibanaMessages(object):
    """Kibana message iterator"""

    def __init__(self, queue, maxBatchSize, timeout):
        self.queue = queue
        self.maxBatchSize = maxBatchSize
        self.end = time.time() + timeout
        self.counter = 0

    def __iter__(self):
        while self.counter < self.maxBatchSize or self.end > time.time():
            self.counter += 1
            try:
                data = self.queue.get(block=False, timeout=0.5)
                if data:
                    yield json.loads(data[0])
            except gevent.queue.Empty:
                break


class KibanaServer(object):
    """Kibana (elasticsearch) server"""

    stopping = False

    def __init__(self, interface, backend, interval=5,
        maxQueueSize=MAX_QUEUE_SIZE, maxBatchSize=MAX_BATCH_SIZE, debug=False):
        _, host, port = parse_addr(interface)
        if port is None:
            self.exit("invalid interface address specified %r" % interface)
        self._interface = (host, port)
        # construct the backend and add hosts to it
        if not backend:
            self.exit("you must specify an (elasticsearch) backend")
        self._backend = p01.kibana.backend.ElasticSearchBackend(self, backend)
        self._interval = float(interval)
        self._maxQueueSize = maxQueueSize
        self._maxBatchSize = maxBatchSize
        self._queue = gevent.queue.Queue(self._maxQueueSize)
        self._scheduler = None
        self._debug = debug
        self._sock = None

    def start(self):
        # register shutdown signals
        gevent.signal(signal.SIGINT, self._shutdown)
        # start accepting connections
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
        self._sock.bind(self._interface)
        # start scheduler
        self._scheduler = Scheduler(self._interval, self._flush)
        # start processing
        while 1:
            try:
                self._process(*self._sock.recvfrom(MAX_PACKET))
            except Exception, ex:
                if self._debug:
                    self.error(str(ex))

    def stop(self):
        self._shutdown()

    def _teardown(self, seconds):
        while seconds:
            sys.stdout.write('%d...' % seconds)
            seconds = seconds - 1
            gevent.sleep(1)

    def _shutdown(self):
        "Shutdown the server"
        if not self.stopping:
            msg = 'Shutdown server, waiting for scheduler...'
            sys.stdout.write(msg)
            self.stopping = gevent.spawn(self._teardown,
                self._scheduler.interval + 1)
            self._scheduler.stop()
            self.stopping.kill()
            self.stopping = None
            self.exit("...Ok\nServer stopped", code=0)

    def _process(self, data, _ignored):
        """Process incoming data"""
        if self._debug:
            self.error('data: %r' % data)
        try:
            # add data to the queue, use tuple for iteration in get()
            self._queue.put((data,), block=False)
        except gevent.queue.Full:
            # that's too much, just throuw away
            pass

    def _flush(self, *args, **kws):
        """Flush log events to server in an elasticsearch batch call"""
        # process data with bulk stream
        try:
            timeout = self._interval - 0.1
            messages = KibanaMessages(self._queue, self._maxBatchSize, timeout)
            self._backend.send(messages)
        except Exception, ex:
            tb = traceback.format_tb(sys.exc_info()[-1])
            self.error(''.join(tb))

    def exit(self, msg, code=1):
        self.error(msg)
        sys.exit(code)

    def error(self, msg):
        sys.stderr.write(msg + '\n')

    def __repr__(self):
        backend = None
        if self._backend is not None:
            backend = self._backend._interface
        return '<%s %s -> %s>' % (self.__class__.__name__, self._interface,
            backend)
