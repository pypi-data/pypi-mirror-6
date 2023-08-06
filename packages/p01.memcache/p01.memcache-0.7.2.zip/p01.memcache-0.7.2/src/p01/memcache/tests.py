##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctestunit import DocFileSuite

import z3c.testing
from p01.memcache import interfaces
from p01.memcache import testing
from p01.memcache import client


class MemcacheClientTest(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return interfaces.IMemcacheClient

    def getTestClass(self):
        return client.MemcacheClient


def test_suite():
    # default tests
    suites = (
        DocFileSuite('README.txt',
            setUp=testing.setUpFakeMemcached,
            tearDown=testing.tearDownFakeMemcached,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        DocFileSuite('ultramemcache.txt',
            setUp=testing.setUpFakeUltraMemcached,
            tearDown=testing.tearDownFakeUltraMemcached,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        DocFileSuite('testing.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        DocTestSuite('p01.memcache.client',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        unittest.makeSuite(MemcacheClientTest),
        )
    # use level 2 tests (--all)
    suite = unittest.TestSuite((
        doctest.DocFileSuite('load-testing.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
    suite.level = 2
    suites += (suite,)
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
