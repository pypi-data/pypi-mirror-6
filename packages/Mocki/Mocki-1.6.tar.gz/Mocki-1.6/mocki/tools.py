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

"""Extra tools used to ease handling of mocks in various contexts :

- AutoMocks : a decorator used to automatically provide mocks to functions,
- Patch : a tool used in with statements to temporary replace static members.

"""
import inspect

from mocki import Mock

class AutoMocks(object):
    """A decorator used to automatically provide mocks to functions.

    To use it, you just need to put this decorator in front of the targeted
    function :
        >>> from mocki import verify

        >>> @AutoMocks
        ... def testSomething(mock, otherMock):
        ...     verify(otherMock).wasAnyCall().invokedOnce()

    Now, each time this function is invoked, its arguments will automatically
    be set with new mocks taking the names of these arguments :
        >>> testSomething()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from otherMock up to now.

    Note that this decorator can also be used from methods :
        >>> class Test(object):
        ...     @AutoMocks
        ...     def testSomething(self, mock, otherMock):
        ...         verify(otherMock).wasAnyCall().invokedOnce()

        >>> test = Test()

        >>> test.testSomething()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from otherMock up to now.

    """
    def __new__(cls, functionOrMethod):
        funcArgs = inspect.getargspec(functionOrMethod).args

        if 'self' in funcArgs and funcArgs.index('self') == 0:
            def decoratedMethod(self):
                return functionOrMethod(self, **{name: Mock(name) for name in funcArgs[1:]})

            # Required for the nose autodiscovery feature to work.
            decoratedMethod.__name__ = functionOrMethod.__name__

            return decoratedMethod
        else:
            def decoratedFunction():
                return functionOrMethod(**{name: Mock(name) for name in funcArgs})

            # Required for the nose autodiscovery feature to work.
            decoratedFunction.__name__ = functionOrMethod.__name__

            return decoratedFunction

class Patch(object):
    """A tool used in with statements to temporary replace static members.

    To use it, you first need a static member to replace :
        >>> class Parent(object):
        ...     @classmethod
        ...     def staticMethod(cls):
        ...         return 'value'

    You also need a placeholder that will temporary replace this static member
    within the with statement, for example, a mock :
        >>> from mocki import Mock

        >>> mock = Mock('theMock')

    Before the with statement, the static member behaves normally :
        >>> Parent.staticMethod()
        'value'

    Within the with statement, the static member loses its normal behavior. It
    is temporary replaced by the provided placeholder :
        >>> from mocki import verify

        >>> with Patch(Parent, 'staticMethod', mock):
        ...     verify(Parent.staticMethod).wasAnyCall().invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from theMock up to now.

    After the with statement, the static member recovers its normal behavior :
        >>> Parent.staticMethod()
        'value'

    If the only thing you want is to replace a static member with a mock, you
    may omit the provided placeholder as well. A new mock taking the name of
    the static member to replace will then be automatically provided :
        >>> with Patch(Parent, 'staticMethod'):
        ...     verify(Parent.staticMethod).wasAnyCall().invokedOnce()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from Parent.staticMethod up to now.

    Note that you can also patch an entire function using the decorator form :
        >>> @Patch(Parent, 'staticMethod')
        ... def testSomething():
        ...     verify(Parent.staticMethod).wasAnyCall().invokedOnce()

        >>> testSomething()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from Parent.staticMethod up to now.

    And of course, the decorator form can also be used from methods :
        >>> class Test(object):
        ...     @Patch(Parent, 'staticMethod')
        ...     def testSomething(self):
        ...         verify(Parent.staticMethod).wasAnyCall().invokedOnce()

        >>> test = Test()

        >>> test.testSomething()
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from Parent.staticMethod up to now.

    """
    def __init__(self, parent, staticMemberName, newValue=None):
        self.parent, self.staticMemberName = parent, staticMemberName

        self.newValue = newValue or Mock('%s.%s' % (self.parent.__name__, self.staticMemberName))

    def __enter__(self):
        self.oldValue = getattr(self.parent, self.staticMemberName)

        setattr(self.parent, self.staticMemberName, self.newValue)

    def __exit__(self, type_, value, traceback):
        setattr(self.parent, self.staticMemberName, self.oldValue)

    def __call__(self, functionOrMethod):
        thisPatch = self

        funcArgs = inspect.getargspec(functionOrMethod).args

        if 'self' in funcArgs and funcArgs.index('self') == 0:
            def decoratedMethod(self, *args, **kwargs):
                with thisPatch:
                    return functionOrMethod(self, *args, **kwargs)

            # Required for the nose autodiscovery feature to work.
            decoratedMethod.__name__ = functionOrMethod.__name__

            return decoratedMethod
        else:
            def decoratedFunction(*args, **kwargs):
                with thisPatch:
                    return functionOrMethod(*args, **kwargs)

            # Required for the nose autodiscovery feature to work.
            decoratedFunction.__name__ = functionOrMethod.__name__

            return decoratedFunction
