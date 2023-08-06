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
"""KibanaServer tests
$Id: test_server.py 3909 2013-12-25 15:40:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

import p01.kibana.server


class KibanaServerTest(unittest.TestCase):

    def setUp(self):
        interface = ':2200'
        backend = ':9200'
        self.svc = p01.kibana.server.KibanaServer(interface, backend)

    def test_construct(self):
        svc = p01.kibana.server.KibanaServer('2200', '9200')
        self.assertEquals(svc._interface, ('', 2200))
        self.assertEquals(svc._interval, 5.0)
        self.assertEquals(svc._debug, 0)
        self.assertEquals(svc._backend._interface, ('', 9200))
        svc = p01.kibana.server.KibanaServer('bar:2200', 'foo:9200', debug=True)
        self.assertEquals(svc._interface, ('bar', 2200))
        self.assertEquals(svc._backend._interface, ('foo', 9200))
        self.assertEquals(svc._debug, True)

    def test_backend(self):
        p01.kibana.server.KibanaServer._send = lambda self, x, y: None
        svc = p01.kibana.server.KibanaServer('2200', 'bar:9200')
        self.assertEquals(svc._backend._interface, ('bar', 9200))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KibanaServerTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


