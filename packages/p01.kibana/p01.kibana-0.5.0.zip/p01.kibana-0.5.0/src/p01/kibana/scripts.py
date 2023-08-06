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
"""Start script and config
$$
"""
__docformat__ = "reStructuredText"

import sys
import socket
import traceback
import optparse

import p01.kibana.server


def get_options(args=None):
    if args is None:
        args = sys.argv
    original_args = args
    parser = optparse.OptionParser(usage=("usage: <script> [options]"))
    parser.add_option('--interface', dest='interface',
        help="interface [host]:port (defaults to :2200)",
        default=':2200',
        )
    parser.add_option('--elasticsearch', dest='elasticsearch',
        help="a elasticsearch backend  [host]:port (defaults to :9700)",
        default=':9700',
        )
    parser.add_option('--interval', dest='interval',
        default=p01.kibana.server.INTERVAL,
        help="flush interval, in seconds (default %s)" % (
            p01.kibana.server.INTERVAL),
        )
    parser.add_option('--max-queue-size', dest='maxQueueSize', type='int',
        help="max (log event) queue size (default=1000)",
        default=p01.kibana.server.MAX_QUEUE_SIZE,
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
        print 'Starting server'
        server = p01.kibana.server.KibanaServer(options.interface,
            options.elasticsearch, interval=options.interval, debug=debug)
        print 'Server started at %s' % options.interface
        server.start()
    except Exception, e:
        sys.stderr.write("interface: %s\n" % options.interface)
        sys.stderr.write("backend: %s\n" % options.elasticsearch)
        sys.stderr.write("interval: %s\n" % options.interval)
        sys.stderr.write("maxQueueSize: %s\n" % options.maxQueueSize)
        sys.stderr.write("debug: %s\n" % options.debug)
        sys.stderr.write("args: %s\n" % sys.argv)
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
