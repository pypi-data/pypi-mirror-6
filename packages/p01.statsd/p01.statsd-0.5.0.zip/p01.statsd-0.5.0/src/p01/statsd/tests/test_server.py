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
"""StatsdServer tests
$Id: test_server.py 3992 2014-03-25 12:47:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

import p01.statsd.server


class StatsdServerTest(unittest.TestCase):

    def setUp(self):
        interface = ':8125'
        backend = ':2003'
        self.svc = p01.statsd.server.StatsdServer(interface, backend)
        self.stats = self.svc._stats

    def test_construct(self):
        svc = p01.statsd.server.StatsdServer('8125', '2003')
        stats = svc._stats
        self.assertEquals(svc._interface, ('', 8125))
        self.assertEquals(svc._interval, 5.0)
        self.assertEquals(svc._debug, 0)
        self.assertEquals(stats.percent, 90.0)
        self.assertEquals(svc._backend._interface, ('', 2003))
        svc = p01.statsd.server.StatsdServer('bar:8125', 'foo:2003', debug=True)
        self.assertEquals(svc._interface, ('bar', 8125))
        self.assertEquals(svc._backend._interface, ('foo', 2003))
        self.assertEquals(svc._debug, True)

    def test_backend(self):
        p01.statsd.server.StatsdServer._send_foo = lambda self, x, y: None
        svc = p01.statsd.server.StatsdServer('8125', 'bar:2003')
        self.assertEquals(svc._backend._interface, ('bar', 2003))

    def test_counters(self):
        pkt = 'foo:1|c'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.counts, {'foo': 1})
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.counts, {'foo': 2})
        pkt = 'foo:-1|c'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.counts, {'foo': 1})

    def test_counters_sampled(self):
        pkt = 'foo:1|c|@.5'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.counts, {'foo': 2})

    def test_timers(self):
        pkt = 'foo:20|ms'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.timers, {'foo': [20.0]})
        pkt = 'foo:10|ms'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.timers, {'foo': [20.0, 10.0]})

    def test_key_sanitize(self):
        pkt = '\t\n#! foo . bar \0 ^:1|c'
        self.svc._process(pkt, None)
        self.assertEquals(self.stats.counts, {'foo.bar': 1})

    def test_key_prefix(self):
        svc = p01.statsd.server.StatsdServer(':8125', ':2003', prefix='pfx')
        pkt = 'foo:1|c'
        svc._process(pkt, None)
        self.assertEquals(svc._stats.counts, {'pfx.foo': 1})


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(StatsdServerTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


