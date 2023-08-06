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
"""Statsd client
$Id: client.py 3992 2014-03-25 12:47:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import random
import socket
import time

INTERFACE = ('127.0.0.1', 8125)


def parse_hostport(spec):
    try:
        parts = spec.split(':')
        if len(parts) == 2:
            return (parts[0], int(parts[1]))
        if len(parts) == 1:
            return ('', int(parts[0]))
    except ValueError, ex:
        raise ValueError("bad backend spec %r: %s" % (spec, ex))
    raise ValueError("expected '[host]:port' but got %r" % spec)


def _format_float(val):
    return ('%f' % val).rstrip('0').rstrip('.')


class StatsdClient(object):
    """Statsd UDP client"""

    def __init__(self, interface=INTERFACE):
        if isinstance(interface, basestring):
            interface = parse_hostport(interface)
        self._interface = interface
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def timer(self, key, timestamp, sample_rate=1):
        self._send('%s:%d|ms' % (key, round(timestamp)), sample_rate)

    def gauge(self, key, value, sample_rate=1):
        self._send('%s:%s|g' % (key, _format_float(value)), sample_rate)

    def incr(self, key, sample_rate=1):
        return self.counter(key, 1, sample_rate)

    increment = incr

    def decr(self, key, sample_rate=1):
        return self.counter(key, -1, sample_rate)

    decrement = decr

    def counter(self, keys, magnitude=1, sample_rate=1):
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        for key in keys:
            self._send('%s:%d|c' % (key, round(magnitude)), sample_rate)

    def _send(self, data, sample_rate=1):
        packet = None
        if sample_rate < 1.0:
            if random.random() < sample_rate:
                packet = data + '|@%s' % sample_rate
        else:
            packet = data
        if packet:
            self._sock.sendto(packet, self._interface)


class StatsCounter(object):

    def __init__(self, client, key, sample_rate=1):
        self._client = client
        self._key = key
        self._sample_rate = sample_rate

    def increment(self):
        self._client.increment(self._key, self._sample_rate)

    def decrement(self):
        self._client.decrement(self._key, self._sample_rate)

    def add(self, val):
        self._client.counter(self._key, val, self._sample_rate)


class StatsTimer(object):

    def __init__(self, client, key):
        self._client = client
        self._key = key
        self._started = 0
        self._timestamp = 0

    def start(self):
        self._started = 1
        self._timestamp = time.time()

    def stop(self):
        if not self._started:
            raise UserWarning("you must call start() before stop(). ignoring.")
            return
        elapsed = time.time() - self._timestamp
        self._client.timer(self._key, int(elapsed * 1000.0))
        self._started = 0


class StatsGauge(object):

    def __init__(self, client, key, sample_rate=1):
        self._client = client
        self._key = key
        self._sample_rate = sample_rate

    def set(self, value):
        self._client.gauge(self._key, value, self._sample_rate)


class Stats(object):

    def __init__(self, client):
        self._client = client

    def get_counter(self, key, sample_rate=1):
        return StatsCounter(self._client, key, sample_rate)

    def get_timer(self, key):
        return StatsTimer(self._client, key)

    def get_gauge(self, key):
        return StatsGauge(self._client, key)


