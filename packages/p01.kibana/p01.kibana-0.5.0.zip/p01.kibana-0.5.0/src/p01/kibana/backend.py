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
"""Elasticsearch upd backend
$Id: backend.py 3921 2014-01-04 23:07:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import sys
from gevent import socket


# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break


def parse_host_port(spec):
    try:
        parts = spec.split(':')
        if len(parts) == 2:
            return (parts[0], int(parts[1]))
        if len(parts) == 1:
            return ('', int(parts[0]))
    except ValueError, ex:
        raise ValueError("bad backend spec %r: %s" % (spec, ex))
    raise ValueError("expected '[host]:port' but got %r" % spec)


class ElasticSearchConnection(object):
    """An udp socket connecting to Elastic Search"""

    def __init__(self, interface):
        self._interface = interface
        self._sock = None

    def __enter__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self

    def __exit__(self, *exc_info):
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None

    def send(self, message):
        self._sock.sendto(message, self._interface)


class ElasticSearchBackend(object):
    """Sends event data to one or more elasticsearch server"""

    def __init__(self, server, interface):
        self.server = server
        self._interface = parse_host_port(interface)

    def error(self, msg):
        sys.stderr.write(msg + '\n')

    def send(self, iterable):
        """Stream logging entries via udp to the elasticsearch server
        
        We received the following data from our client:

        {
            '_index': '...',
            '_type': '...',
            '_source': {
                '@version': '...',
                '@timestamp': '...',
                'message': '...'
            }
        }

        """
        with ElasticSearchConnection(self._interface) as connection:
            for data in iterable:
                meta = {
                    'index': {
                        '_index': data['_index'],
                        '_type':  data['_type'],
                        },
                    }
                source = data['_source']
                try:
                    message = '\n'.join([
                        json.dumps(meta),
                        json.dumps(source),
                        # force ending line break
                        '',
                    ])
                except TypeError:
                    continue
                if hasattr(message, 'encode'):
                    message = message.encode('utf-8')
                connection.send(message)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self._interface)
