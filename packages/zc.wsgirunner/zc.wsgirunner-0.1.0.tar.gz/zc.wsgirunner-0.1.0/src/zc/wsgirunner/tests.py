##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import setupstack

import doctest
import unittest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock

class App:

    def __init__(self, glob, **kw):
        self.glob = glob
        self.kw = kw

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__, sorted(self.glob), self.kw)

class Server(App):

    def __call__(self, app):
        print("%r\nserving\n%r" % (self, app))

def test_config1(default, **kw):
    _test_config("test_config1", default, kw)

def test_config2(default, **kw):
    _test_config("test_config2", default, kw)

def test_config3(default, **kw):
    _test_config("test_config3", default, kw)

def _test_config(name, default, kw):
    print("%s(%r, %r)" % (name, sorted(default), kw))

def setUp(test):
    setupstack.setUpDirectory(test)
    setupstack.context_manager(test, mock.patch('logging.basicConfig'))
    setupstack.context_manager(test, mock.patch('ZConfig.configureLoggers'))

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'main.test',
            setUp=setUp, tearDown=setupstack.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

