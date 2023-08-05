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

class MatcherTest(unittest.TestCase):
    def checkTrue(self, *args, **kwargs):
        self.assertTrue(self.matcher(self.FakeCallInvocation(*args, **kwargs)))

    def checkFalse(self, *args, **kwargs):
        self.assertFalse(self.matcher(self.FakeCallInvocation(*args, **kwargs)))

    class FakeCallInvocation(object):
        def __new__(cls, *args, **kwargs):
            return collections.namedtuple('FakeCallInvocation', 'args kwargs')(args, kwargs)

class AnyCallTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import AnyCall

        self.matcher = AnyCall()

    def testWithNoArgOrKwarg(self):
        self.checkTrue()

    def testWithArgsButNoKwarg(self):
        self.checkTrue(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkTrue(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkTrue(1, 2, 3, x=7, y=8, z=9)

class CallWithNoArgOrKwargTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call()

    def testWithNoArgOrKwarg(self):
        self.checkTrue()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithArgsButNoKwargUsingValuesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(1, 2, 3)

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkTrue(1, 2, 3)

    def testWithDifferentArgsButNoKwarg(self):
        self.checkFalse(7, 8, 9)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithArgsButNoKwargUsingMatchersTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(EqualMatcher(1), EqualMatcher(2), EqualMatcher(3))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkTrue(1, 2, 3)

    def testWithDifferentArgsButNoKwarg(self):
        self.checkFalse(7, 8, 9)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithArgsButNoKwargUsingCallablesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(EqualCallable(1), EqualCallable(2), EqualCallable(3))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkTrue(1, 2, 3)

    def testWithDifferentArgsButNoKwarg(self):
        self.checkFalse(7, 8, 9)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithKwargsButNoArgUsingValuesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(x=7, y=8, z=9)

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkTrue(x=7, y=8, z=9)

    def testWithDifferentKwargsButNoArg(self):
        self.checkFalse(x=1, y=2, z=3)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithKwargsButNoArgUsingMatchersTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(x=EqualMatcher(7), y=EqualMatcher(8), z=EqualMatcher(9))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkTrue(x=7, y=8, z=9)

    def testWithDifferentKwargsButNoArg(self):
        self.checkFalse(x=1, y=2, z=3)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithKwargsButNoArgUsingCallablesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(x=EqualCallable(7), y=EqualCallable(8), z=EqualCallable(9))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkTrue(x=7, y=8, z=9)

    def testWithDifferentKwargsButNoArg(self):
        self.checkFalse(x=1, y=2, z=3)

    def testWithArgsAndKwargs(self):
        self.checkFalse(1, 2, 3, x=7, y=8, z=9)

class CallWithArgsAndKwargsUsingValuesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(1, 2, 3, x=7, y=8, z=9)

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkTrue(1, 2, 3, x=7, y=8, z=9)

    def testWithDifferentArgsAndKwargs(self):
        self.checkFalse(7, 8, 9, x=1, y=2, z=3)

class CallWithArgsAndKwargsUsingMatchersTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(EqualMatcher(1), EqualMatcher(2), EqualMatcher(3),
                            x=EqualMatcher(7), y=EqualMatcher(8), z=EqualMatcher(9))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkTrue(1, 2, 3, x=7, y=8, z=9)

    def testWithDifferentArgsAndKwargs(self):
        self.checkFalse(7, 8, 9, x=1, y=2, z=3)

class CallWithArgsAndKwargsUsingCallablesTest(MatcherTest):
    def setUp(self):
        from mocki.matchers import Call

        self.matcher = Call(EqualCallable(1), EqualCallable(2), EqualCallable(3),
                            x=EqualCallable(7), y=EqualCallable(8), z=EqualCallable(9))

    def testWithNoArgOrKwarg(self):
        self.checkFalse()

    def testWithArgsButNoKwarg(self):
        self.checkFalse(1, 2, 3)

    def testWithKwargsButNoArg(self):
        self.checkFalse(x=7, y=8, z=9)

    def testWithArgsAndKwargs(self):
        self.checkTrue(1, 2, 3, x=7, y=8, z=9)

    def testWithDifferentArgsAndKwargs(self):
        self.checkFalse(7, 8, 9, x=1, y=2, z=3)

class EqualCallable(object):
    def __init__(self, expectedValue):
        self.expectedValue = expectedValue

    def __call__(self, value):
        return value == self.expectedValue

class EqualMatcher(object):
    def __init__(self, expectedValue):
        self.expectedValue = expectedValue

    def matches(self, value):
        return value == self.expectedValue
