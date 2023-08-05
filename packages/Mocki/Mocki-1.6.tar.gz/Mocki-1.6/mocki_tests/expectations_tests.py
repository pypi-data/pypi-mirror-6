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

class ExpectationTest(unittest.TestCase):
    def checkTrue(self, nbCallInvocations):
        self.assertTrue(self.expectation(self.FakeCallInvocations(nbCallInvocations)))

    def checkFalse(self, nbCallInvocations):
        self.assertFalse(self.expectation(self.FakeCallInvocations(nbCallInvocations)))

    class FakeCallInvocations(object):
        def __new__(cls, nbCallInvocations):
            return [collections.namedtuple('FakeCallInvocation', 'i')(i) for i in range(nbCallInvocations)]

class AtLeastTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import AtLeast

        self.expectation = AtLeast(1)

    def testWithNoCallInvocation(self):
        self.checkFalse(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkTrue(nbCallInvocations=2)

class AtLeastOnceTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import AtLeastOnce

        self.expectation = AtLeastOnce()

    def testWithNoCallInvocation(self):
        self.checkFalse(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkTrue(nbCallInvocations=2)

class AtMostTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import AtMost

        self.expectation = AtMost(1)

    def testWithNoCallInvocation(self):
        self.checkTrue(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkFalse(nbCallInvocations=2)

class AtMostOnceTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import AtMostOnce

        self.expectation = AtMostOnce()

    def testWithNoCallInvocation(self):
        self.checkTrue(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkFalse(nbCallInvocations=2)

class BetweenTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import Between

        self.expectation = Between(1, 3)

    def testWithNoCallInvocation(self):
        self.checkFalse(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkTrue(nbCallInvocations=2)

    def testWith3CallInvocations(self):
        self.checkTrue(nbCallInvocations=3)

    def testWith4CallInvocations(self):
        self.checkFalse(nbCallInvocations=4)

class ExactlyTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import Exactly

        self.expectation = Exactly(1)

    def testWithNoCallInvocation(self):
        self.checkFalse(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkFalse(nbCallInvocations=2)

class NeverTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import Never

        self.expectation = Never()

    def testWithNoCallInvocation(self):
        self.checkTrue(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkFalse(nbCallInvocations=1)

class OnceTest(ExpectationTest):
    def setUp(self):
        from mocki.expectations import Once

        self.expectation = Once()

    def testWithNoCallInvocation(self):
        self.checkFalse(nbCallInvocations=0)

    def testWithOneCallInvocation(self):
        self.checkTrue(nbCallInvocations=1)

    def testWith2CallInvocations(self):
        self.checkFalse(nbCallInvocations=2)
