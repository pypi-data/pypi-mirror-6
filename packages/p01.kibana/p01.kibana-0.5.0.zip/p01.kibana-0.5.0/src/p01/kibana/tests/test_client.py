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
"""KibanaClient tests
$Id: test_client.py 3909 2013-12-25 15:40:42Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import unittest

import p01.kibana.client


class FakeClient(p01.kibana.client.KibanaClient):
    """Cleint wrapper with fake _send method"""

    def __init__(self, hostport=None):
        super(FakeClient, self).__init__(hostport)
        self.results = []

    def send(self, data=None, **kwargs):
        if data is not None:
            kwargs.update(data)
        self.results.append(kwargs)


class KibanaClientTest(unittest.TestCase):

    def setUp(self):
        self.client = FakeClient()

    def test_send(self):
        data = {
            '_index': '...',
            '_type': '...',
            '_source': {
                '@version': '...',
                '@timestamp': '...',
                'message': '...'
            }
        }
        self.client.send(foo='foo', bar=u'bar')
        self.assertEquals(self.client.results[-1], {'bar': u'bar', 'foo': 'foo'})

    def test_send_kwargs(self):
        data = {'message': 'empty'}
        self.client.send(data)
        self.assertEquals(self.client.results[-1], {'message': 'empty'})


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(KibanaClientTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
