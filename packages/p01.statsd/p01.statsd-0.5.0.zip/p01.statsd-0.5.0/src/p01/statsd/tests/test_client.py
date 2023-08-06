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
"""StatsdClient tests
$Id: test_client.py 3992 2014-03-25 12:47:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

import p01.statsd.client


class FakeClient(p01.statsd.client.StatsdClient):
    """Cleint wrapper with fake _send method"""

    def __init__(self, hostport=None):
        super(FakeClient, self).__init__(hostport)
        self.packets = []

    def _send(self, data, sample_rate=1):
        self.packets.append((data, sample_rate))


class StatsdClientTest(unittest.TestCase):

    def setUp(self):
        self._cli = FakeClient()

    def test_timer(self):
        self._cli.timer('foo', 15, 1)
        self.assertEquals(self._cli.packets[-1], ('foo:15|ms', 1))
        self._cli.timer('bar.baz', 1.35, 1)
        self.assertEquals(self._cli.packets[-1], ('bar.baz:1|ms', 1))
        self._cli.timer('x', 1.99, 1)
        self.assertEquals(self._cli.packets[-1], ('x:2|ms', 1))
        self._cli.timer('x', 1, 0.5)
        self.assertEquals(self._cli.packets[-1], ('x:1|ms', 0.5))

    def test_increment(self):
        self._cli.increment('foo')
        self.assertEquals(self._cli.packets[-1], ('foo:1|c', 1))
        self._cli.increment('x', 0.5)
        self.assertEquals(self._cli.packets[-1], ('x:1|c', 0.5))

    def test_decrement(self):
        self._cli.decrement('foo')
        self.assertEquals(self._cli.packets[-1], ('foo:-1|c', 1))
        self._cli.decrement('x', 0.2)
        self.assertEquals(self._cli.packets[-1], ('x:-1|c', 0.2))

    def test_counter(self):
        self._cli.counter('foo', 5)
        self.assertEquals(self._cli.packets[-1], ('foo:5|c', 1))
        self._cli.counter('foo', -50)
        self.assertEquals(self._cli.packets[-1], ('foo:-50|c', 1))
        self._cli.counter('foo', 5.9)
        self.assertEquals(self._cli.packets[-1], ('foo:6|c', 1))
        self._cli.counter('foo', 1, 0.2)
        self.assertEquals(self._cli.packets[-1], ('foo:1|c', 0.2))

    def test_gauge(self):
        self._cli.gauge('foo', 5)
        self.assertEquals(self._cli.packets[-1], ('foo:5|g', 1))
        self._cli.gauge('foo', -50)
        self.assertEquals(self._cli.packets[-1], ('foo:-50|g', 1))
        self._cli.gauge('foo', 5.9)
        self.assertEquals(self._cli.packets[-1], ('foo:5.9|g', 1))


class StatsTest(unittest.TestCase):

    def setUp(self):
        self._cli = FakeClient()
        self._stat = p01.statsd.client.Stats(self._cli)

    def test_timer(self):
        timer = self._stat.get_timer('foo')
        timer.start()
        timer.stop()
        data, sr = self._cli.packets[-1]
        pkt = data.split(':')
        self.assertEquals(pkt[0], 'foo')

        # ensure warning is raised for mismatched start/stop
        timer = self._stat.get_timer('foo')
        self.assertRaises(UserWarning, timer.stop)

    def test_counter(self):
        count = self._stat.get_counter('foo')
        count.increment()
        count.decrement()
        count.add(5)
        self.assertEquals(self._cli.packets[-1], ('foo:5|c', 1))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(StatsdClientTest),
        unittest.makeSuite(StatsTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
