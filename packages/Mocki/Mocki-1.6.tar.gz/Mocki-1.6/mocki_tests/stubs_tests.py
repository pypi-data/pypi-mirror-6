#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
#   more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with Mocki. If not, see <http://www.gnu.org/licenses/>.
#

import collections, unittest

class StubCallerMixin(object):
    def callStub(self, callInvocationName):
        class FakeCallInvocation(object):
            def __new__(cls, name):
                return collections.namedtuple('FakeCallInvocation', 'name')(name)

        return self.stub(FakeCallInvocation(callInvocationName))

class ReturnTest(unittest.TestCase, StubCallerMixin):
    def setUp(self):
        from mocki.stubs import Return

        self.stub = Return('value')

    def test(self):
        self.assertEqual(self.callStub(callInvocationName='call'), 'value')

class RaiseTest(unittest.TestCase, StubCallerMixin):
    def setUp(self):
        from mocki.stubs import Raise

        self.stub = Raise(Exception('error'))

    def test(self):
        with self.assertRaisesRegexp(Exception, 'error'):
            self.callStub(callInvocationName='call')

class InOrderTest(unittest.TestCase, StubCallerMixin):
    def setUp(self):
        from mocki.stubs import InOrder

        self.stub = InOrder(self.Stub(beforeCallInvocationName='stub'),
                            self.Stub(beforeCallInvocationName='otherStub'))

    def test(self):
        self.assertEqual(self.callStub(callInvocationName='1stCall'), 'stub-1stCall')
        self.assertEqual(self.callStub(callInvocationName='2ndCall'), 'otherStub-2ndCall')
        self.assertEqual(self.callStub(callInvocationName='nthCall'), 'otherStub-nthCall')

    class Stub(object):
        def __init__(self, beforeCallInvocationName):
            self.beforeCallInvocationName = beforeCallInvocationName

        def __call__(self, callInvocation):
            return '%s-%s' % (self.beforeCallInvocationName, callInvocation.name)
