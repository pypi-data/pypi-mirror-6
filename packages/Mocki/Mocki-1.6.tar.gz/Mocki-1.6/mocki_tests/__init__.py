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

class MockBasedTest(object):
    def __new__(cls, mockName, mockResolver=lambda mock: mock):
        class MockSetUpTest(unittest.TestCase):
            def setUp(self):
                from mocki import Mock

                self.mock = mockResolver(Mock(mockName))

        return MockSetUpTest

class StubTestTemplate(object):
    def test(self):
        self.stubMockToReturnValue('newValue')
        self.stubMockToReturnValue('otherNewValue')

        self.checkMockNotStubbedToReturnValue('value')

        self.checkMockStubbedToReturnValue('newValue')
        self.checkMockStubbedToReturnValue('otherNewValue')

    def stubMockToReturnValue(self, valueToReturn):
        from mocki import stub

        class ReturnValue(object):
            def __call__(self, callInvocation):
                return callInvocation.kwargs['valueToReturn']

        stub(self.mock).on(MatchingCallInvocation(self.mock, valueToReturn=valueToReturn)).do(ReturnValue())

    def checkMockNotStubbedToReturnValue(self, valueToReturn):
        self.assertIsNone(self.mock(valueToReturn=valueToReturn))

    def checkMockStubbedToReturnValue(self, valueToReturn):
        self.assertEqual(self.mock(valueToReturn=valueToReturn), valueToReturn)

class StubMockTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock),

    StubTestTemplate
): pass

class StubMockMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member),

    StubTestTemplate
): pass

class StubMockMemberMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member.member),

    StubTestTemplate
): pass

class NamedCallsInvokerMixin(object):
    def invokeNamedCalls(self, *names):
        for name in names:
            self.mock(name=name)

class VerifyTestTemplate(object):
    def __new__(cls, mockName):
        class VerifyTestTemplate(NamedCallsInvokerMixin):
            def testWithNoCallInvoked(self):
                self.checkNamedCallNotInvokedExactly('2ndCall', nTimes=10, message='\n'.join([
                    'No call invoked from %s up to now.' % mockName
                ]))

            def testWithNoMatchingCallAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '3rdCall')

                self.checkNamedCallInvokedExactly('2ndCall', nTimes=0)

            def testWithNoMatchingCallNotAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '3rdCall')

                self.checkNamedCallNotInvokedExactly('2ndCall', nTimes=10, message='\n'.join([
                    'Found no matching call invoked from %s up to now :' % mockName,
                    r"  %s\(name='1stCall'\)" % mockName,
                    r"  %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithOneMatchingCallAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedExactly('2ndCall', nTimes=1)

            def testWithOneMatchingCallNotAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallNotInvokedExactly('2ndCall', nTimes=10, message='\n'.join([
                    'Found one matching call invoked from %s up to now :' % mockName,
                    r"  %s\(name='1stCall'\)" % mockName,
                    r"> %s\(name='2ndCall'\)" % mockName,
                    r"  %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithSeveralMatchingCallsAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '2ndCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedExactly('2ndCall', nTimes=2)

            def testWithSeveralMatchingCallsNotAsExpected(self):
                from mocki import verify

                self.invokeNamedCalls('1stCall', '2ndCall', '2ndCall', '3rdCall')

                self.checkNamedCallNotInvokedExactly('2ndCall', nTimes=10, message='\n'.join([
                    'Found 2 matching calls invoked from %s up to now :' % mockName,
                    r"  %s\(name='1stCall'\)" % mockName,
                    r"> %s\(name='2ndCall'\)" % mockName,
                    r"> %s\(name='2ndCall'\)" % mockName,
                    r"  %s\(name='3rdCall'\)" % mockName
                ]))

            def checkNamedCallInvokedExactly(self, name, nTimes):
                from mocki import verify

                verify(self.mock).was(MatchingCallInvocation(self.mock, name=name)).invoked(self.Exactly(nTimes))

            def checkNamedCallNotInvokedExactly(self, name, nTimes, message):
                from mocki import verify

                with self.assertRaisesRegexp(AssertionError, message):
                    verify(self.mock).was(MatchingCallInvocation(self.mock, name=name)).invoked(self.Exactly(nTimes))

            class Exactly(object):
                def __init__(self, nTimes):
                    self.nTimes = nTimes

                def __call__(self, callInvocations):
                    return len(callInvocations) == self.nTimes

        return VerifyTestTemplate

class VerifyFromMockTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock),

    VerifyTestTemplate(mockName='theMock')
): pass

class VerifyFromMockMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member),

    VerifyTestTemplate(mockName='theMock.member')
): pass

class VerifyFromMockMemberMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member.member),

    VerifyTestTemplate(mockName='theMock.member.member')
): pass

class VerifyInOrderTestTemplate(object):
    def __new__(cls, mockName):
        class VerifyInOrderTestTemplate(NamedCallsInvokerMixin):
            def testWithNoCallInvoked(self):
                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'No call invoked from %s up to now.' % mockName
                ]))

            def testWithNoVerifiedCallInvocation(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('2ndCall')

            def testWithPrecedingVerifiedCallInvocationWithNoMatchingCall(self):
                self.invokeNamedCalls('1stCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('1stCall')

                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'Found no matching call invoked from %s up to now :' % mockName,
                    r"x   %s\(name='1stCall'\)" % mockName,
                    r"    %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithPrecedingVerifiedCallInvocationWithOneMatchingCall(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('1stCall')

                self.checkNamedCallInvokedInOrder('2ndCall')

            def testWithPrecedingVerifiedCallInvocationWithSeveralMatchingCalls(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('1stCall')

                self.checkNamedCallInvokedInOrder('2ndCall')
                self.checkNamedCallInvokedInOrder('2ndCall')

            def testWithAlreadyVerifiedCallInvocationWithOneMatchingCall(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('2ndCall')

                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'Found one matching call invoked from %s up to now, but not in order :' % mockName,
                    r"    %s\(name='1stCall'\)" % mockName,
                    r"x - %s\(name='2ndCall'\)" % mockName,
                    r"    %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithAlreadyVerifiedCallInvocationWithSeveralMatchingCalls(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('2ndCall')

                self.checkNamedCallInvokedInOrder('2ndCall')

            def testWithFollowingVerifiedCallInvocationWithNoMatchingCall(self):
                self.invokeNamedCalls('1stCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('3rdCall')

                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'Found no matching call invoked from %s up to now :' % mockName,
                    r"    %s\(name='1stCall'\)" % mockName,
                    r"x   %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithFollowingVerifiedCallInvocationWithOneMatchingCall(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('3rdCall')

                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'Found one matching call invoked from %s up to now, but not in order :' % mockName,
                    r"    %s\(name='1stCall'\)" % mockName,
                    r"  - %s\(name='2ndCall'\)" % mockName,
                    r"x   %s\(name='3rdCall'\)" % mockName
                ]))

            def testWithFollowingVerifiedCallInvocationWithSeveralMatchingCalls(self):
                self.invokeNamedCalls('1stCall', '2ndCall', '2ndCall', '3rdCall')

                self.checkNamedCallInvokedInOrder('3rdCall')

                self.checkNamedCallNotInvokedInOrder('2ndCall', message='\n'.join([
                    'Found 2 matching calls invoked from %s up to now, but not in order :' % mockName,
                    r"    %s\(name='1stCall'\)" % mockName,
                    r"  - %s\(name='2ndCall'\)" % mockName,
                    r"  - %s\(name='2ndCall'\)" % mockName,
                    r"x   %s\(name='3rdCall'\)" % mockName
                ]))

            def checkNamedCallInvokedInOrder(self, name):
                from mocki import verify

                verify(self.mock).was(MatchingCallInvocation(self.mock, name=name)).invokedInOrder()

            def checkNamedCallNotInvokedInOrder(self, name, message):
                from mocki import verify

                with self.assertRaisesRegexp(AssertionError, message):
                    verify(self.mock).was(MatchingCallInvocation(self.mock, name=name)).invokedInOrder()

        return VerifyInOrderTestTemplate

class VerifyInOrderFromMockTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock),

    VerifyInOrderTestTemplate(mockName='theMock')
): pass

class VerifyInOrderFromMockMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member),

    VerifyInOrderTestTemplate(mockName='theMock.member')
): pass

class VerifyInOrderFromMockMemberMemberTest(
    MockBasedTest(mockName='theMock', mockResolver=lambda mock: mock.member.member),

    VerifyInOrderTestTemplate(mockName='theMock.member.member')
): pass

class VerifyInOrderFromDifferentMockMembersTest(MockBasedTest('theMock')):
    def testWithPrecedingVerifiedCallInvocation(self):
        self.invokeNamedCalls('member', '1stCall', 'otherMember', '2ndCall', 'member', '3rdCall')

        self.checkNamedCallInvokedInOrder('member', '1stCall')

        self.checkNamedCallInvokedInOrder('otherMember', '2ndCall')

    def testWithAlreadyVerifiedCallInvocation(self):
        self.invokeNamedCalls('member', '1stCall', 'otherMember', '2ndCall', 'member', '3rdCall')

        self.checkNamedCallInvokedInOrder('otherMember', '2ndCall')

        self.checkNamedCallNotInvokedInOrder('otherMember', '2ndCall', message='\n'.join([
            'Found one matching call invoked from theMock.otherMember up to now, but not in order :',
            r"    theMock.member\(name='1stCall'\)",
            r"x - theMock.otherMember\(name='2ndCall'\)",
            r"    theMock.member\(name='3rdCall'\)"
        ]))

    def testWithFollowingVerifiedCallInvocation(self):
        self.invokeNamedCalls('member', '1stCall', 'otherMember', '2ndCall', 'member', '3rdCall')

        self.checkNamedCallInvokedInOrder('member', '3rdCall')

        self.checkNamedCallNotInvokedInOrder('otherMember', '2ndCall', message='\n'.join([
            'Found one matching call invoked from theMock.otherMember up to now, but not in order :',
            r"    theMock.member\(name='1stCall'\)",
            r"  - theMock.otherMember\(name='2ndCall'\)",
            r"x   theMock.member\(name='3rdCall'\)"
        ]))

    def invokeNamedCalls(self, *namesByMockMembersNames):
        for mockMemberName, name in zip(namesByMockMembersNames[0::2], namesByMockMembersNames[1::2]):
            mockMember = getattr(self.mock, mockMemberName)

            mockMember(name=name)

    def checkNamedCallInvokedInOrder(self, mockMemberName, name):
        from mocki import verify

        mockMember = getattr(self.mock, mockMemberName)

        verify(mockMember).was(MatchingCallInvocation(mockMember, name=name)).invokedInOrder()

    def checkNamedCallNotInvokedInOrder(self, mockMemberName, name, message):
        from mocki import verify

        mockMember = getattr(self.mock, mockMemberName)

        with self.assertRaisesRegexp(AssertionError, message):
            verify(mockMember).was(MatchingCallInvocation(mockMember, name=name)).invokedInOrder()

class FakeCallInvocationsProviderMixin(object):
    def callInvocations(self, nbCallInvocations):
        class FakeCallInvocations(object):
            def __new__(cls, nbCallInvocations):
                return [collections.namedtuple('FakeCallInvocation', 'i')(i) for i in range(nbCallInvocations)]

        self.callInvocations = FakeCallInvocations(nbCallInvocations)

        return self.callInvocations

class CallInvocationHistoryTest(unittest.TestCase, FakeCallInvocationsProviderMixin):
    def checkCallInvocations(self, callInvocations, expectedIndices):
        self.assertEqual(callInvocations, [callInvocation for callInvocation in self.callInvocations if callInvocation.i in expectedIndices])

    def checkStr(self, expectedStr):
        self.assertEqual(str(self.history), expectedStr)

class MatchingCallInvocationHistoryTest(CallInvocationHistoryTest):
    def setUp(self):
        from mocki import MatchingCallInvocationHistory

        matcher = lambda callInvocation: callInvocation.i in (0, 2)

        self.history = MatchingCallInvocationHistory(self.callInvocations(3), matcher)

    def testGetCallInvocations(self):
        self.checkCallInvocations(self.history.callInvocations, (0, 1, 2))

    def testGetMatchingIndices(self):
        self.assertEqual(self.history.matchingIndices, (0, 2))

    def testGetMatchingCallInvocations(self):
        self.checkCallInvocations(self.history.matchingCallInvocations, (0, 2))

    def testStr(self):
        self.checkStr('\n'.join([
            '> FakeCallInvocation(i=0)',
            '  FakeCallInvocation(i=1)',
            '> FakeCallInvocation(i=2)'
        ]))

class InOrderMatchingCallInvocationHistoryWithVerifiedIndicesTest(CallInvocationHistoryTest):
    def setUp(self):
        from mocki import InOrderMatchingCallInvocationHistory

        matcher = lambda callInvocation: callInvocation.i in (1, 3, 5)

        self.history = InOrderMatchingCallInvocationHistory(self.callInvocations(6), matcher, verifiedIndices=(2, 3))

    def testGetCallInvocations(self):
        self.checkCallInvocations(self.history.callInvocations, (0, 1, 2, 3, 4, 5))

    def testGetMatchingIndices(self):
        self.assertEqual(self.history.matchingIndices, (1, 3, 5))

    def testGetMatchingCallInvocations(self):
        self.checkCallInvocations(self.history.matchingCallInvocations, (1, 3, 5))

    def testGetVerifiedIndices(self):
        self.assertEqual(self.history.verifiedIndices, (2, 3))

    def testGetVerifiedCallInvocations(self):
        self.checkCallInvocations(self.history.verifiedCallInvocations, (2, 3))

    def testGetMatchingButNonVerifiedIndices(self):
        self.assertEqual(self.history.matchingButNonVerifiedIndices, (5,))

    def testGetMatchingButNonVerifiedCallInvocations(self):
        self.checkCallInvocations(self.history.matchingButNonVerifiedCallInvocations, (5,))

    def testStr(self):
        self.checkStr('\n'.join([
            '    FakeCallInvocation(i=0)',
            '  - FakeCallInvocation(i=1)',
            'x   FakeCallInvocation(i=2)',
            'x - FakeCallInvocation(i=3)',
            '    FakeCallInvocation(i=4)',
            '  > FakeCallInvocation(i=5)'
        ]))

class InOrderMatchingCallInvocationHistoryWithNoVerifiedIndicesTest(CallInvocationHistoryTest):
    def setUp(self):
        from mocki import InOrderMatchingCallInvocationHistory

        matcher = lambda callInvocation: callInvocation.i in (0, 2)

        self.history = InOrderMatchingCallInvocationHistory(self.callInvocations(3), matcher, verifiedIndices=())

    def testGetCallInvocations(self):
        self.checkCallInvocations(self.history.callInvocations, (0, 1, 2))

    def testGetMatchingIndices(self):
        self.assertEqual(self.history.matchingIndices, (0, 2))

    def testGetMatchingCallInvocations(self):
        self.checkCallInvocations(self.history.matchingCallInvocations, (0, 2))

    def testGetVerifiedIndices(self):
        self.assertEqual(self.history.verifiedIndices, ())

    def testGetVerifiedCallInvocations(self):
        self.checkCallInvocations(self.history.verifiedCallInvocations, ())

    def testGetMatchingButNonVerifiedIndices(self):
        self.assertEqual(self.history.matchingButNonVerifiedIndices, (0, 2))

    def testGetMatchingButNonVerifiedCallInvocations(self):
        self.checkCallInvocations(self.history.matchingButNonVerifiedCallInvocations, (0, 2))

    def testStr(self):
        self.checkStr('\n'.join([
            '  > FakeCallInvocation(i=0)',
            '    FakeCallInvocation(i=1)',
            '  > FakeCallInvocation(i=2)'
        ]))

class MockProviderMixin(object):
    def mock(self, name):
        from mocki import Mock

        self.mock = Mock(name)

        return self.mock

class CallInvocationTest(unittest.TestCase):
    def checkAsTupleMatchingTo(self, mock, *args, **kwargs):
        self.assertEqual(self.callInvocation[0], mock)
        self.assertEqual(self.callInvocation[1], args)
        self.assertEqual(self.callInvocation[2], kwargs)

    def checkAsNamedTupleMatchingTo(self, mock, *args, **kwargs):
        self.assertEqual(self.callInvocation.mock, mock)
        self.assertEqual(self.callInvocation.args, args)
        self.assertEqual(self.callInvocation.kwargs, kwargs)

    def checkStr(self, expectedStr):
        self.assertEqual(str(self.callInvocation), expectedStr)

class CallInvocationWithNoArgOrKwargTest(CallInvocationTest, MockProviderMixin):
    def setUp(self):
        from mocki import CallInvocation

        self.callInvocation = CallInvocation(self.mock('theMock'))

    def testAsTuple(self):
        self.checkAsTupleMatchingTo(self.mock)

    def testAsNamedTuple(self):
        self.checkAsNamedTupleMatchingTo(self.mock)

    def testStr(self):
        self.checkStr('theMock()')

class CallInvocationWithArgsButNoKwargTest(CallInvocationTest, MockProviderMixin):
    def setUp(self):
        from mocki import CallInvocation

        self.callInvocation = CallInvocation(self.mock('theMock'), 1, 2.0, '300')

    def testAsTuple(self):
        self.checkAsTupleMatchingTo(self.mock, 1, 2.0, '300')

    def testAsNamedTuple(self):
        self.checkAsNamedTupleMatchingTo(self.mock, 1, 2.0, '300')

    def testStr(self):
        self.checkStr("theMock(1, 2.0, '300')")

class CallInvocationWithKwargsButNoArgTest(CallInvocationTest, MockProviderMixin):
    def setUp(self):
        from mocki import CallInvocation

        self.callInvocation = CallInvocation(self.mock('theMock'), x=7, y=8.0, z='900')

    def testAsTuple(self):
        self.checkAsTupleMatchingTo(self.mock, x=7, y=8.0, z='900')

    def testAsNamedTuple(self):
        self.checkAsNamedTupleMatchingTo(self.mock, x=7, y=8.0, z='900')

    def testStr(self):
        self.checkStr("theMock(x=7, y=8.0, z='900')")

class CallInvocationWithArgsAndKwargsTest(CallInvocationTest, MockProviderMixin):
    def setUp(self):
        from mocki import CallInvocation

        self.callInvocation = CallInvocation(self.mock('theMock'), 1, 2.0, '300', x=7, y=8.0, z='900')

    def testAsTuple(self):
        self.checkAsTupleMatchingTo(self.mock, 1, 2.0, '300', x=7, y=8.0, z='900')

    def testAsNamedTuple(self):
        self.checkAsNamedTupleMatchingTo(self.mock, 1, 2.0, '300', x=7, y=8.0, z='900')

    def testStr(self):
        self.checkStr("theMock(1, 2.0, '300', x=7, y=8.0, z='900')")

class MatchingCallInvocation(object):
    def __init__(self, mock, *args, **kwargs):
        self.mock, self.args, self.kwargs = mock, args, kwargs

    def __call__(self, callInvocation):
        return ((self.mock, self.args, self.kwargs) ==
                (callInvocation.mock, callInvocation.args, callInvocation.kwargs))
