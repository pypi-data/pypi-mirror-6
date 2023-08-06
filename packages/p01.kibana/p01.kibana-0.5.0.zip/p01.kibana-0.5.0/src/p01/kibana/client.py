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
"""Kibana (elasticsearch) client
$Id: client.py 3919 2014-01-04 06:42:48Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime
try:
    from gevent import socket
except ImportError:
    import socket

# priority: ujson > simplejson > jsonlib2 > json
priority = ['ujson', 'simplejson', 'jsonlib2', 'json']
for mod in priority:
    try:
        json = __import__(mod)
    except ImportError:
        pass
    else:
        break

INTERFACE = ('127.0.0.1', 2200)


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


class KibanaClient(object):
    """Kibana client"""

    def __init__(self, interface=None, index='missing', type='missing'):
        if interface is None:
            interface = INTERFACE
        if isinstance(interface, basestring):
            interface = parse_host_port(interface)
        self._interface = interface
        self._version = 1
        self._index = index
        self._type = type
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message=None, index=None, type=None, **kwargs):
        """We will send a formatted json string via udp based on the given data

        {
            '_index': '...',
            '_type': '...',
            '_source': {
                '@version': '...',
                '@timestamp': '...',
                'message': '...',
                '...': '...',
            }
        }
        """
        _index = index or self._index
        _type = type or self._type
        # ensure required event data
        kwargs['@version'] = self._version
        kwargs['@timestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'
        if message is not None:
            kwargs['message'] = message
        data = {
            # elasticsearch bulk meta data
            '_index': _index,
            '_type': _type,
            '_source': kwargs,
            }
        data = json.dumps(data)
        self._sock.sendto(data, self._interface)
