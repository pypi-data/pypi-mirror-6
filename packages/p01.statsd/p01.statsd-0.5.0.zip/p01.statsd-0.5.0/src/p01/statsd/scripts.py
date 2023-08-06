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
"""Start script and cinfig
$Id: scripts.py 3992 2014-03-25 12:47:22Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
import traceback
import optparse

import p01.statsd.server


def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser(usage=("usage: statsd [options]"))
    parser.add_option('--interface', dest='interface',
        help="interface [host]:port (defaults to :8125)",
        default=':8125',
        )
    parser.add_option('--graphite', dest='graphite',
        help="a graphite backend  [host]:port (defaults to :2003)",
        default=':2003',
        )
    parser.add_option('--interval', dest='interval',
        default=p01.statsd.server.INTERVAL,
        help="flush interval, in seconds (default %s)" % (
            p01.statsd.server.INTERVAL),
        )
    parser.add_option('--prefix', dest='prefix',
        help="prefix added to all keys (default None)",
        default='',
        )
    parser.add_option('--percent', dest='percent',
        help="percent threshold (default %s)" % (p01.statsd.server.PERCENT),
        default=p01.statsd.server.PERCENT,
        )
    parser.add_option('--debug', dest='debug', type='int',
        help="debug marker (default=False)",
        default=0,
        )
    options, positional = parser.parse_args(args)
    options.original_args = original_args
    return options


def main(args=None):
    options = get_options(args)
    if options.debug:
        debug = True
    else:
        debug = False
    try:
        # stops with signal.SIGINT on KeyboardInterrupt
        server = p01.statsd.server.StatsdServer(options.interface,
            options.graphite, interval=options.interval, percent=options.percent,
            prefix=options.prefix, debug=debug)
        server.start()
    except Exception, e:
        sys.stderr.write("interface: %s\n" % options.interface)
        sys.stderr.write("backend: %s\n" % options.graphite)
        sys.stderr.write("interval: %s\n" % options.interval)
        sys.stderr.write("prefix: %s\n" % options.prefix)
        sys.stderr.write("percent: %s\n" % options.percent)
        sys.stderr.write("debug: %s\n" % options.debug)
        sys.stderr.write("args: %s\n" % sys.argv)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
