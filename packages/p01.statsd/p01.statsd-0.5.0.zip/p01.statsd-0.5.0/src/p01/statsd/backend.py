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
"""Graphite backend
$Id: backend.py 3992 2014-03-25 12:47:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import cStringIO
import sys
import time

from gevent import socket


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


class GraphiteBackend(object):
    """Sends stats to one or more Graphite servers"""

    def __init__(self, interface):
        self._interface = parse_hostport(interface)

    def error(self, msg):
        sys.stderr.write(msg + '\n')

    # XXX: add support for N retries
    def _send(self, buf):
        """Send io buffer to graphite"""
        # flush stats to graphite
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self._interface)
            sock.sendall(buf.getvalue())
            sock.close()
        except Exception, ex:
            self.error("failed to send stats to graphite %s: %s" % (
                self._interface, ex))

    def send(self, stats):
        "Format stats and send to one or more Graphite hosts"
        buf = cStringIO.StringIO()
        now = int(time.time())
        num_stats = 0

        # timer stats
        pct = stats.percent
        timers = stats.timers
        for key, vals in timers.iteritems():
            if not vals:
                continue

            # compute statistics
            num = len(vals)
            vals = sorted(vals)
            vmin = vals[0]
            vmax = vals[-1]
            mean = vmin
            max_at_thresh = vmax
            if num > 1:
                idx = round((pct / 100.0) * num)
                tmp = vals[:int(idx)]
                if tmp:
                    max_at_thresh = tmp[-1]
                    mean = sum(tmp) / idx

            key = 'stats.timers.%s' % key
            buf.write('%s.mean %f %d\n' % (key, mean, now))
            buf.write('%s.upper %f %d\n' % (key, vmax, now))
            buf.write('%s.upper_%d %f %d\n' % (key, pct, max_at_thresh, now))
            buf.write('%s.lower %f %d\n' % (key, vmin, now))
            buf.write('%s.count %d %d\n' % (key, num, now))
            num_stats += 1

        # counter stats
        counts = stats.counts
        for key, val in counts.iteritems():
            buf.write('stats.%s %f %d\n' % (key, val / stats.interval, now))
            buf.write('stats_counts.%s %f %d\n' % (key, val, now))
            num_stats += 1

        # counter stats
        gauges = stats.gauges
        for key, val in gauges.iteritems():
            buf.write('stats.%s %f %d\n' % (key, val, now))
            buf.write('stats_counts.%s %f %d\n' % (key, val, now))
            num_stats += 1

        buf.write('statsd.numStats %d %d\n' % (num_stats, now))

        self._send(buf)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._interface)
