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

"""A matcher is a callable that returns true if the invocation given to it
comply with the particular condition the matcher is built for. It is intended
to be used in verifications and stubs. In verifications, it filters the call
invocations on which the expectation will be applied. In stubs, it is used to
determine whether or not the corresponding stub must be performed on a given
call invocation.

To use it, you first need a mock to verify :
    >>> from mocki import Mock

    >>> mock = Mock('theMock')

Then, here is how to verify whether or not this mock was invoked once :
    >>> from mocki import verify

    >>> verify(mock).was(lambda callInvocation: True).invokedOnce()
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

Of course, for such a simple condition, defining your own custom matcher is
not necessary. You can use the corresponding built-in matcher as well :
    >>> verify(mock).wasAnyCall().invokedOnce()
    Traceback (most recent call last):
    ...
    AssertionError: No call invoked from theMock up to now.

Matchers can also be used from stubs. E.g., here is how to stub the mock to
return a given value on any call invocation made from it :
    >>> from mocki import stub

    >>> stub(mock).on(lambda callInvocation: True).doReturn('value')

Now, any call invocation made from it will return the value 'value' :
    >>> mock('call')
    'value'

    >>> mock('otherCall')
    'value'

Again, for such a simple condition, defining your own custom matcher is not
necessary. You can use the corresponding built-in matcher as well  :
    >>> stub(mock).onAnyCall().doReturn('value')

    >>> mock('call')
    'value'

    >>> mock('otherCall')
    'value'

"""
class AnyCall(object):
    """A matcher that matches any call invocation.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, invoke some calls from it :
        >>> mock('call')
        >>> mock('otherCall')

    We can now ask to verify whether or not any call was invoked from it :
        >>> from mocki import verify

        >>> verify(mock).wasAnyCall().invokedExactly(2)

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating the problem :
        >>> verify(mock).wasAnyCall().invokedExactly(3)
        Traceback (most recent call last):
        ...
        AssertionError: Found 2 matching calls invoked from theMock up to now :
        > theMock('call')
        > theMock('otherCall')

    Matchers can also be used from stubs. E.g., here is how to stub the mock to
    return a given value on any call invocation made from it :
        >>> from mocki import stub

        >>> stub(mock).onAnyCall().doReturn('value')

    Now, any call invocation made from it will return the value 'value' :
        >>> mock('call')
        'value'

        >>> mock('otherCall')
        'value'

    """
    def __call__(self, callInvocation):
        return True

class Call(object):
    """A matcher that matches call invocations with given args and kwargs.

    To use it, you first need a mock to verify :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, invoke some calls from it :
        >>> mock()
        >>> mock(1, 2, 3)
        >>> mock(x=7, y=8, z=9)
        >>> mock(1, 2, 3, x=7, y=8, z=9)

    We can now ask to verify whether or not some given calls were invoked from
    it, either using values, callables (i.e. any callable that takes a value)
    or argument matchers (i.e. any object having a method named 'matches' that
    takes a value, like the ones provided by Hamcrest) :
        >>> from hamcrest import equal_to

        >>> from mocki import verify

        >>> verify(mock).wasCall().invokedOnce()

        >>> verify(mock).wasCall(1, 2, lambda value: value == 3).invokedOnce()

        >>> verify(mock).wasCall(x=7, y=8, z=lambda value: value == 9).invokedOnce()

        >>> verify(mock).wasCall(1, 2, equal_to(3), x=7, y=8, z=equal_to(9)).invokedOnce()

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

    Matchers can also be used from stubs. E.g., here is how to stub the mock to
    return given values on given call invocations made from it :
        >>> from mocki import stub

        >>> stub(mock).onCall('call').doReturn('value')
        >>> stub(mock).onCall('otherCall').doReturn('otherValue')

    Now, any call invocation made from it matching to the first call will
    return the value 'value', while any one matching to the other call will
    return the value 'otherValue' :
        >>> mock('call')
        'value'

        >>> mock('otherCall')
        'otherValue'

    """
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def __call__(self, callInvocation):
        class Placeholder(object):
            def __init__(self, expectedValue):
                self.expectedValue = expectedValue

            def __eq__(self, value):
                if hasattr(self.expectedValue, 'matches'):
                    return self.expectedValue.matches(value)
                elif hasattr(self.expectedValue, '__call__'):
                    return self.expectedValue(value)
                else:
                    return self.expectedValue == value

        return ((callInvocation.args, callInvocation.kwargs) ==
                (tuple([Placeholder(arg) for arg in self.args]),
                 dict([(name, Placeholder(kwarg)) for name, kwarg in self.kwargs.items()])))
