###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH and Contributors.
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
"""Statsd server
$Id: server.py 3992 2014-03-25 12:47:22Z roger.ineichen $
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
from collections import defaultdict

import gevent
import gevent.socket
from gevent.thread import allocate_lock as Lock

import p01.statsd.backend


socket = gevent.socket

stats_lock = Lock()

# constants
INTERVAL = 5.0
PERCENT = 90.0
MAX_PACKET = 2048


# table to remove invalid characters from keys
ALL_ASCII = set(chr(c) for c in range(256))
KEY_VALID = string.ascii_letters + string.digits + '_-.'
KEY_TABLE = string.maketrans(KEY_VALID + '/', KEY_VALID + '_')
KEY_DELETIONS = ''.join(ALL_ASCII.difference(KEY_VALID + '/'))


class Stats(object):

    def __init__(self):
        self.timers = defaultdict(list)
        self.counts = defaultdict(float)
        self.gauges = defaultdict(float)
        self.percent = PERCENT
        self.interval = INTERVAL


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


class StatsdServer(object):
    """Statsd server"""

    def __init__(self, interface, backend, interval=5, percent=90, prefix='',
        debug=False):
        _, host, port = parse_addr(interface)
        if port is None:
            self.exit("invalid interface address specified %r" % interface)
        self._interface = (host, port)
        # construct the backend and add hosts to it
        if not backend:
            self.exit("you must specify a (graphite) backend")
        self._backend = p01.statsd.backend.GraphiteBackend(backend)
        self._percent = float(percent)
        self._interval = float(interval)
        self._debug = debug
        self._sock = None
        self._flush_task = None
        self._prefix = prefix
        self._reset_stats()

    def _reset_stats(self):
        with stats_lock:
            self._stats = Stats()
            self._stats.percent = self._percent
            self._stats.interval = self._interval

    def exit(self, msg, code=1):
        self.error(msg)
        sys.exit(code)

    def error(self, msg):
        sys.stderr.write(msg + '\n')

    def start(self):
        "Start the service"
        # register signals
        gevent.signal(signal.SIGINT, self._shutdown)

        # spawn the flush trigger
        def _flush_impl():
            while 1:
                gevent.sleep(self._stats.interval)

                # rotate stats
                stats = self._stats
                self._reset_stats()

                # send the stats to the backends which in turn broadcasts
                # the stats packet to one or more hosts.
                try:
                    self._backend.send(stats)
                except Exception, ex:
                    trace = traceback.format_tb(sys.exc_info()[-1])
                    self.error(''.join(trace))

        self._flush_task = gevent.spawn(_flush_impl)

        # start accepting connections
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
        self._sock.bind(self._interface)
        while 1:
            try:
                self._process(*self._sock.recvfrom(MAX_PACKET))
            except Exception, ex:
                self.error(str(ex))

    def _shutdown(self):
        "Shutdown the server"
        self.exit("Server exiting", code=0)

    def _process(self, data, _):
        "Process a single packet and update the internal tables."
        parts = data.split(':')
        if self._debug:
            self.error('packet: %r' % data)
        if not parts:
            return

        # interpret the packet and update stats
        stats = self._stats
        key = parts[0].translate(KEY_TABLE, KEY_DELETIONS)
        if self._prefix:
            key = '.'.join([self._prefix, key])
        for part in parts[1:]:
            srate = 1.0
            fields = part.split('|')
            length = len(fields)
            if length < 2:
                continue
            value = fields[0]
            stype = fields[1].strip()

            with stats_lock:
                # timer (milliseconds)
                if stype == 'ms':
                    stats.timers[key].append(float(value if value else 0))

                # counter with optional sample rate
                elif stype == 'c':
                    if length == 3 and fields[2].startswith('@'):
                        srate = float(fields[2][1:])
                    value = float(value if value else 1) * (1 / srate)
                    stats.counts[key] += value
                elif stype == 'g':
                    value = float(value if value else 1)
                    stats.gauges[key] = value

    def __repr__(self):
        backend = None
        if self._backend is not None:
            backend = self._backend._interface
        return '<%s %s -> %s>' % (self.__class__.__name__, self._interface,
            backend)
