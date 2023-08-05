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

"""An easy-to-use but full featured mocking library for Python.

Here is how to start working with Mocki :
    >>> from mocki import verify

    >>> mock = Mock('theMock')

    >>> verify(mock).wasCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

    >>> mock(1, 2, 3, x=7, y=8, z=9)

    >>> verify(mock).wasCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()

"""
import collections

class Mock(object):
    """A mock is a callable object that is able to track any call invoked from
    it and that will automatically provide on-fly generated mock members from
    each non existing member accessed.

    To use it, first instanciate a mock giving it a name, then invoke some
    calls from it, with or without args and kwargs :
        >>> mock = Mock('theMock')

        >>> mock()
        >>> mock(1, 2, 3)
        >>> mock(x=7, y=8, z=9)
        >>> mock(1, 2, 3, x=7, y=8, z=9)

    Now, we can ask to verify whether or not given calls were invoked from it :
        >>> from mocki import verify

        >>> verify(mock).wasCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating where the problem is :
        >>> verify(mock).wasCall(7, 8, 9, x=1, y=2, z=3).invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock up to now :
          theMock()
          theMock(1, 2, 3)
          theMock(x=7, y=8, z=9)
          theMock(1, 2, 3, x=7, y=8, z=9)

    You can also invoke some calls from mock members :
        >>> mock = Mock('theMock')

        >>> mock.method()
        >>> mock.otherMethod(1, 2, 3)
        >>> mock.method(x=7, y=8, z=9)
        >>> mock.otherMethod(1, 2, 3, x=7, y=8, z=9)

    Now, we can ask to verify whether or not given calls were invoked from any
    of these mock members :
        >>> verify(mock.otherMethod).wasCall(1, 2, 3, x=7, y=8, z=9).invokedOnce()

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating where the problem is :
        >>> verify(mock.otherMethod).wasCall(7, 8, 9, x=1, y=2, z=3).invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock.otherMethod up to now :
          theMock.method()
          theMock.otherMethod(1, 2, 3)
          theMock.method(x=7, y=8, z=9)
          theMock.otherMethod(1, 2, 3, x=7, y=8, z=9)

    It must be noted that the mock members and their parent mock all shares the
    same history, which here explains why the debugging-friendly message is
    showing us call invocations made from other mock members. Sharing histories
    may be interesting when using the in order verifications.

    Actually, since mock members are mocks themselves, everything possible on
    mocks is also possible on their members. And everything possible on their
    members is also possible their members members, and so on...

    """
    def __init__(self, mockName, callInvocations=None, verifiedIndices=None):
        self._mockName = mockName

        self._callInvocations = callInvocations if callInvocations is not None else []
        self._verifiedIndices = verifiedIndices if verifiedIndices is not None else []

        self._headStubbing = lambda *args, **kwargs: None

    def __call__(self, *args, **kwargs):
        self._callInvocations.append(CallInvocation(self, *args, **kwargs))

        return self._headStubbing(*args, **kwargs)

    def __getattr__(self, mockMemberName):
        mockMember = self.__class__('%s.%s' % (self._mockName, mockMemberName), self._callInvocations, self._verifiedIndices)

        setattr(self, mockMemberName, mockMember)

        return mockMember

def stub(mock):
    """A function used to stub a given mock.

    To use it, you first need a mock to stub :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, stub it as desired. E.g., here is how to stub the mock to return a
    given value on any call invocation made from it :
        >>> stub(mock).onAnyCall().doReturn('value')

    Now, any call invocation made from it will return the value 'value' :
        >>> mock('call')
        'value'

        >>> mock('otherCall')
        'value'

    Sometimes, it can be useful to override a stubbing with a more specific
    one. This can simply be done by defining the more specific stubbing after
    the global case. E.g., here is how to define a more specific stubbing in
    case the mock is called with the argument 'specificCall' :
        >>> stub(mock).onCall('specificCall').doReturn('specificValue')

    Now, in this specific case, the value 'specificValue' will be return, while
    any other call invocation will still return the value 'value' :
        >>> mock('call')
        'value'

        >>> mock('specificCall')
        'specificValue'

    """
    class OnStatement(object):
        def __init__(self, mock):
            self.mock = mock

        def on(self, matcher):
            class DoStatement(object):
                def __init__(self, mock, matcher):
                    self.mock, self.matcher = mock, matcher

                def do(self, stub):
                    class Stubbing(object):
                        def __init__(self, mock, matcher, stub, nextStubbing):
                            self.mock, self.matcher, self.stub, self.nextStubbing = mock, matcher, stub, nextStubbing

                        def __call__(self, *args, **kwargs):
                            invocation = CallInvocation(self.mock, *args, **kwargs)

                            if self.matcher(invocation):
                                return self.stub(invocation)
                            else:
                                return self.nextStubbing(*args, **kwargs)

                    self.mock._headStubbing = Stubbing(self.mock, self.matcher, stub, self.mock._headStubbing)

                def __getattr__(self, name):
                    from mocki import stubs

                    for stubName, Stub in stubs.__dict__.items():
                        if name == '%s%s' % (self.do.__name__, stubName):
                            return lambda *args, **kwargs: self.do(Stub(*args, **kwargs))

                    raise AttributeError

            return DoStatement(mock, matcher)

        def __getattr__(self, name):
            from mocki import matchers

            for matcherName, Matcher in matchers.__dict__.items():
                if name == '%s%s' % (self.on.__name__, matcherName):
                    return lambda *args, **kwargs: self.on(Matcher(*args, **kwargs))

            raise AttributeError

    return OnStatement(mock)

def verify(mock):
    """A function used to verify whether or not a given call was invoked from a
    given mock.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    If we ask to verify whether or not a 2nd call was invoked from the mock, an
    assertion error will be raised with a debugging-friendly message indicating
    that no call has been invoked from it up to now :
        >>> verify(mock).wasCall('2ndCall').invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    Now, invoke some calls from it :
        >>> mock('1stCall')
        >>> mock('2ndCall')
        >>> mock('1stCall')

    If we ask again to verify whether or not a 2nd call was invoked, no more
    assertion error will be raised, which indicates that this 2nd call was
    invoked as expected :
        >>> verify(mock).wasCall('2ndCall').invokedOnce()

    If we ask for the opposite, an assertion error will be raised again :
        >>> from mocki.expectations import Never

        >>> verify(mock).wasCall('2ndCall').invokedNever()
        Traceback (most recent call last):
        ...
        AssertionError: Found one matching call invoked from theMock up to now :
          theMock('1stCall')
        > theMock('2ndCall')
          theMock('1stCall')

    What is interesting here is the debugging-friendly message attached to the
    assertion error. It clearly shows us which calls were invoked from the mock
    up to now, and among them, which ones are matching with our verification
    statement.

    Here are some other examples :
        >>> verify(mock).wasCall('1stCall').invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('1stCall')
          theMock('2ndCall')
        > theMock('1stCall')

        >>> verify(mock).wasCall('3rdCall').invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock up to now :
          theMock('1stCall')
          theMock('2ndCall')
          theMock('1stCall')

    Sometimes, it can be very useful to verify that some calls were invoked in
    a particular order. This is done with the in order verifications.

    An important thing to known about the in order verifications is that we can
    only use these verifications on mocks that share the same parent. Actually,
    this is not a big problem, since we can safely instantiate mocks from other
    mocks :
        >>> mock = Mock('theMock')

        >>> method, otherMethod = mock.method, mock.otherMethod

    If we ask to verify whether or not a 2nd call was invoked from one of these
    mocks, an assertion error will be raised with a debugging-friendly message
    indicating that no call has been invoked from it up to now :
        >>> verify(otherMethod).wasCall('2ndCall').invokedInOrder()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock.otherMethod up to now.

    Now, invoke some calls from them :
        >>> method('1stCall')
        >>> otherMethod('2ndCall')
        >>> method('1stCall')

    If we ask again to verify whether or not a 2nd call was invoked, no more
    assertion error will be raised, which indicates that this 2nd call was
    invoked as expected :
        >>> verify(otherMethod).wasCall('2ndCall').invokedInOrder()

    But, if we verify this condition twice, an assertion error will be raised
    again, since no other 2nd call was invoked meanwhile :
        >>> verify(otherMethod).wasCall('2ndCall').invokedInOrder()
        Traceback (most recent call last):
        ...
        AssertionError: Found one matching call invoked from theMock.otherMethod up to now, but not in order :
            theMock.method('1stCall')
        x - theMock.otherMethod('2ndCall')
            theMock.method('1stCall')

    What is interesting here is the debugging-friendly message attached to the
    assertion error. It clearly shows us which calls were invoked from the mock
    up to now, and among them, which ones were already verified and which ones
    are matching with our verification statement.

    Here are some other examples :
        >>> verify(method).wasCall('1stCall').invokedInOrder()

        >>> verify(method).wasCall('1stCall').invokedInOrder()
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock.method up to now, but not in order :
          - theMock.method('1stCall')
        x   theMock.otherMethod('2ndCall')
        x - theMock.method('1stCall')

        >>> verify(method).wasCall('3rdCall').invokedInOrder()
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock.method up to now :
            theMock.method('1stCall')
        x   theMock.otherMethod('2ndCall')
        x   theMock.method('1stCall')

    """
    class WasStatement(object):
        def __init__(self, mock):
            self.mock = mock

        def was(self, matcher):
            class InvokedStatement(object):
                def __init__(self, mock, matcher):
                    self.mock, self.matcher = mock, matcher

                def invoked(self, expectation):
                    matcher = lambda callInvocation: callInvocation.mock is self.mock and self.matcher(callInvocation)

                    history = MatchingCallInvocationHistory(self.mock._callInvocations, matcher)

                    if not expectation(history.matchingCallInvocations):
                        if len(history.callInvocations) == 0:
                            raise AssertionError('No call invoked from %s up to now.' %
                                                 (self.mock._mockName,))
                        else:
                            if len(history.matchingCallInvocations) == 0:
                                raise AssertionError('Found no matching call invoked from %s up to now :\n%s' %
                                                     (self.mock._mockName, history))
                            elif len(history.matchingCallInvocations) == 1:
                                raise AssertionError('Found one matching call invoked from %s up to now :\n%s' %
                                                     (self.mock._mockName, history))
                            else:
                                raise AssertionError('Found %s matching calls invoked from %s up to now :\n%s' %
                                                     (len(history.matchingCallInvocations), self.mock._mockName, history))

                def invokedInOrder(self):
                    matcher = lambda callInvocation: callInvocation.mock is self.mock and self.matcher(callInvocation)

                    history = InOrderMatchingCallInvocationHistory(self.mock._callInvocations, matcher, self.mock._verifiedIndices)

                    if len(history.matchingButNonVerifiedIndices) > 0:
                        self.mock._verifiedIndices.append(history.matchingButNonVerifiedIndices[0])
                    else:
                        if len(history.callInvocations) == 0:
                            raise AssertionError('No call invoked from %s up to now.' %
                                                 (self.mock._mockName,))
                        else:
                            if len(history.matchingCallInvocations) == 0:
                                raise AssertionError('Found no matching call invoked from %s up to now :\n%s' %
                                                     (self.mock._mockName, history))
                            elif len(history.matchingCallInvocations) == 1:
                                raise AssertionError('Found one matching call invoked from %s up to now, but not in order :\n%s' %
                                                     (self.mock._mockName, history))
                            else:
                                raise AssertionError('Found %s matching calls invoked from %s up to now, but not in order :\n%s' %
                                                     (len(history.matchingCallInvocations), self.mock._mockName, history))

                def __getattr__(self, name):
                    from mocki import expectations

                    for expectationName, Expectation in expectations.__dict__.items():
                        if name == '%s%s' % (self.invoked.__name__, expectationName):
                            return lambda *args, **kwargs: self.invoked(Expectation(*args, **kwargs))

                    raise AttributeError

            return InvokedStatement(self.mock, matcher)

        def __getattr__(self, name):
            from mocki import matchers

            for matcherName, Matcher in matchers.__dict__.items():
                if name == '%s%s' % (self.was.__name__, matcherName):
                    return lambda *args, **kwargs: self.was(Matcher(*args, **kwargs))

            raise AttributeError

    return WasStatement(mock)

class MatchingCallInvocationHistory(object):
    def __init__(self, callInvocations, matcher):
        self.callInvocations, self.matcher = callInvocations, matcher

    @property
    def matchingIndices(self):
        return tuple([index for index, callInvocation in enumerate(self.callInvocations) if self.matcher(callInvocation)])

    @property
    def matchingCallInvocations(self):
        return [self.callInvocations[index] for index in self.matchingIndices]

    def __str__(self):
        def getHistoryLinesStrs():
            for index, invocation in enumerate(self.callInvocations):
                if index in self.matchingIndices:
                    yield '> %s' % (invocation,)
                else:
                    yield '  %s' % (invocation,)

        return '\n'.join(getHistoryLinesStrs())

class InOrderMatchingCallInvocationHistory(object):
    def __init__(self, callInvocations, matcher, verifiedIndices):
        self.callInvocations, self.matcher, self.verifiedIndices = callInvocations, matcher, verifiedIndices

    @property
    def matchingIndices(self):
        return tuple([index for index, callInvocation in enumerate(self.callInvocations) if self.matcher(callInvocation)])

    @property
    def matchingCallInvocations(self):
        return [self.callInvocations[index] for index in self.matchingIndices]

    @property
    def verifiedCallInvocations(self):
        return [self.callInvocations[index] for index in self.verifiedIndices]

    @property
    def matchingButNonVerifiedIndices(self):
        if len(self.verifiedIndices) > 0:
            return tuple([index for index in self.matchingIndices if index > max(self.verifiedIndices)])
        else:
            return self.matchingIndices

    @property
    def matchingButNonVerifiedCallInvocations(self):
        return [self.callInvocations[index] for index in self.matchingButNonVerifiedIndices]

    def __str__(self):
        def getHistoryLinesStrs():
            for index, invocation in enumerate(self.callInvocations):
                if index in self.matchingIndices:
                    if index in self.verifiedIndices:
                        yield 'x - %s' % (invocation,)
                    elif index in self.matchingButNonVerifiedIndices:
                        yield '  > %s' % (invocation,)
                    else:
                        yield '  - %s' % (invocation,)
                else:
                    if index in self.verifiedIndices:
                        yield 'x   %s' % (invocation,)
                    else:
                        yield '    %s' % (invocation,)

        return '\n'.join(getHistoryLinesStrs())

class CallInvocation(object):
    def __new__(cls, mock, *args, **kwargs):
        class CallInvocation(collections.namedtuple('CallInvocation', 'mock args kwargs')):
            def __str__(self):
                def getArgsAsCsvStr():
                    return ', '.join(['%r' % arg for arg in self.args])

                def getKwargsAsCsvStr():
                    return ', '.join(['%s=%r' % kwarg for kwarg in sorted(self.kwargs.items())])

                if len(self.args) > 0 and len(self.kwargs) > 0:
                    return ('%s(%s, %s)' % (self.mock._mockName, getArgsAsCsvStr(), getKwargsAsCsvStr()))
                elif len(self.args) > 0:
                    return ('%s(%s)' % (self.mock._mockName, getArgsAsCsvStr()))
                elif len(self.kwargs) > 0:
                    return ('%s(%s)' % (self.mock._mockName, getKwargsAsCsvStr()))
                else:
                    return '%s()' % (self.mock._mockName,)

        return CallInvocation(mock, args, kwargs)
