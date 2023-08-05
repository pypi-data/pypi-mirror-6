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

"""An expectation is a callable that returns true if the matching invocations
given to it comply with the particular condition the expectation is built for.
It is intended to be used in verifications, where it acts as an assertion
applied on the invocations filtered by the matcher.

To use it, you first need a mock to verify :
    >>> from mocki import Mock

    >>> mock = Mock('theMock')

Then, here is how to use a custom expectation to verify whether or not this
mock was invoked once :
    >>> from mocki import verify

    >>> verify(mock).wasAnyCall().invoked(lambda invocations: len(invocations) == 1)
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

Of course, for such a simple condition, defining your own custom expectation is
not necessary. You can use the corresponding built-in expectation as well :
    >>> verify(mock).wasAnyCall().invokedOnce()
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

"""
class AtLeast(object):
    """An expectation that returns true when there is at least N matching
    invocations, where N is the parameter given to it.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at least 1 time :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedAtLeast(1)
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedAtLeast(1)

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedAtLeast(1)

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, callInvocations):
        return len(callInvocations) >= self.nTimes

class AtLeastOnce(object):
    """An expectation that returns true when there is at least one matching
    invocation.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at least once :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedAtLeastOnce()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedAtLeastOnce()

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedAtLeastOnce()

    """
    def __call__(self, callInvocations):
        return len(callInvocations) >= 1

class AtMost(object):
    """An expectation that returns true when there is at most N matching
    invocations, where N is the parameter given to it.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at most 1 time :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedAtMost(1)

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedAtMost(1)

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedAtMost(1)
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('1stCall')
        > theMock('2ndCall')

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, callInvocations):
        return len(callInvocations) <= self.nTimes

class AtMostOnce(object):
    """An expectation that returns true when there is at most one matching
    invocation.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked at most once :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedAtMostOnce()

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedAtMostOnce()

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedAtMostOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('1stCall')
        > theMock('2ndCall')

    """
    def __call__(self, callInvocations):
        return len(callInvocations) <= 1

class Between(object):
    """An expectation that returns true when there is between N and M matching
    invocations, where N and M are the parameters given to it.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked between 1 and 3 times :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedBetween(1, 3)
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedBetween(1, 3)

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedBetween(1, 3)

    ...With 3 calls invoked :
        >>> mock('3rdCall')

        >>> verify(mock).wasAnyCall().invokedBetween(1, 3)

    With 4 calls invoked :
        >>> mock('4thCall')

        >>> verify(mock).wasAnyCall().invokedBetween(1, 3)
        Traceback (most recent call last):
        ...
        AssertionError: Found 4 matching calls invoked from theMock up to now :
        > theMock('1stCall')
        > theMock('2ndCall')
        > theMock('3rdCall')
        > theMock('4thCall')

    """
    def __init__(self, nTimes, mTimes):
        self.nTimes, self.mTimes = nTimes, mTimes

    def __call__(self, callInvocations):
        return len(callInvocations) >= self.nTimes and len(callInvocations) <= self.mTimes

class Exactly(object):
    """An expectation that returns true when there is exactly N matching
    invocations, where N is the parameter given to it.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked exactly 1 time :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedExactly(1)
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedExactly(1)

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedExactly(1)
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('1stCall')
        > theMock('2ndCall')

    """
    def __init__(self, nTimes):
        self.nTimes = nTimes

    def __call__(self, callInvocations):
        return len(callInvocations) == self.nTimes

class Never(object):
    """An expectation that returns true when there is no matching invocation.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was never invoked :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedNever()

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedNever()
        Traceback (most recent call last):
        ...
        AssertionError: Found one matching call invoked from theMock up to now :
        > theMock('1stCall')

    """
    def __call__(self, callInvocations):
        return len(callInvocations) == 0

class Once(object):
    """An expectation that returns true when there is one matching invocation.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    With no call invoked, here is what we get when we ask to verify whether or
    not the mock was invoked once :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    ...With one call invoked :
        >>> mock('1stCall')

        >>> verify(mock).wasAnyCall().invokedOnce()

    ...With 2 calls invoked :
        >>> mock('2ndCall')

        >>> verify(mock).wasAnyCall().invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('1stCall')
        > theMock('2ndCall')

    """
    def __call__(self, callInvocations):
        return len(callInvocations) == 1
