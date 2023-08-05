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

"""A stub is a callable that performs the particular action it is built for on
the matching invocations given to it.

To use it, you first need a mock to stub :
    >>> from mocki import Mock

    >>> mock = Mock('theMock')

Then, stub it as desired. E.g., here is how to stub this mock to return a given
value on any call invocation made from it :
    >>> from mocki import stub

    >>> stub(mock).onAnyCall().do(lambda callInvocation: 'value')

Now, any call invocation made from it will return the value 'value' :
    >>> mock('call')
    'value'

Of course, for such a simple action, defining your own custom stub is not
necessary. You can use the corresponding built-in stub as well :
    >>> stub(mock).onAnyCall().doReturn('value')

    >>> mock('call')
    'value'

"""
class Return(object):
    """A stub that returns a given value.

    To use it, you first need a mock to stub :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, stub it to return a given value :
        >>> from mocki import stub

        >>> stub(mock).onAnyCall().doReturn('value')

    Now, any call invocation made from it will return this value :
        >>> mock('call')
        'value'

    """
    def __init__(self, value):
        self.value = value

    def __call__(self, callInvocation):
        return self.value

class Raise(object):
    """A stub that raises a given exception.

    To use it, you first need a mock to stub :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, stub it to raise a given exception :
        >>> from mocki import stub

        >>> stub(mock).onAnyCall().doRaise(Exception('error'))

    Now, any call invocation made from it will return this exception :
        >>> mock('call')
        Traceback (most recent call last):
        ...
        Exception: error

    """
    def __init__(self, exception):
        self.exception = exception

    def __call__(self, callInvocation):
        raise self.exception

class InOrder(object):
    """A stub that describes a sequence of stubs that will be applied in order,
    for each matching invocation given to it, the last stub being repeatedly
    applied on any further matching invocation.

    To use it, you first need a mock to stub :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Then, stub it to follow a given sequence of stubs :
        >>> from mocki import stub

        >>> stub(mock).onAnyCall().doInOrder(Return('value'), Return('otherValue'))

    Now, the 1st call invocation made from it will return the value 'value',
    while the 2nd one will return the value 'otherValue', this last value being
    then repeatedly returned on any further matching invocation :
        >>> mock('1stCall')
        'value'

        >>> mock('2ndCall')
        'otherValue'

        >>> mock('nthCall')
        'otherValue'

    """
    def __init__(self, stub, *stubs):
        self.stubs = [stub] + list(stubs)

        self.stubsIter = iter(self.stubs)

    def __call__(self, callInvocation):
        try:
            return next(self.stubsIter)(callInvocation)
        except StopIteration:
            return self.stubs[-1](callInvocation)
