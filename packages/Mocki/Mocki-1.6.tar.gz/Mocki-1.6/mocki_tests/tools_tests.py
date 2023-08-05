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

import unittest

import mocki.tools

class AutoMocksTest(unittest.TestCase):
    def setUp(self):
        self.mockBak = mocki.tools.Mock

        mocki.tools.Mock = lambda name: name

    def tearDown(self):
        mocki.tools.Mock = self.mockBak

class AutoMocksDecoratorFromFunctionTest(AutoMocksTest):
    def test(self):
        from mocki.tools import AutoMocks

        @AutoMocks
        def returnGivenMocks(mock, otherMock):
            return (mock, otherMock)

        self.assertEqual(returnGivenMocks(), ('mock', 'otherMock'))

class AutoMocksDecoratorFromMethodTest(AutoMocksTest):
    def test(self):
        from mocki.tools import AutoMocks

        class Test(object):
            @AutoMocks
            def returnGivenMocks(self, mock, otherMock):
                return (mock, otherMock)

        self.assertEqual(Test().returnGivenMocks(), ('mock', 'otherMock'))

class PatchTest(unittest.TestCase):
    def setUp(self):
        self.mockBak = mocki.tools.Mock

        mocki.tools.Mock = lambda name: name

        self.Static.member = 'oldValue'

    def tearDown(self):
        mocki.tools.Mock = self.mockBak

        del self.Static.member

    def checkStaticMemberUnchanged(self):
        self.assertEqual(self.Static.member, 'oldValue')

    def checkStaticMemberChangedTo(self, value):
        self.assertEqual(self.Static.member, value)

    class Static(object): pass

    class StaticMemberPatch(object):
        def __new__(cls, *args, **kwargs):
            from mocki.tools import Patch

            return Patch(PatchTest.Static, 'member', *args, **kwargs)

class PatchStatementTest(PatchTest):
    def testWithNewValue(self):
        from mocki.tools import Patch

        self.checkStaticMemberUnchanged()

        with self.StaticMemberPatch('newValue'):
            self.checkStaticMemberChangedTo('newValue')

        self.checkStaticMemberUnchanged()

    def testWithNoNewValue(self):
        from mocki.tools import Patch

        self.checkStaticMemberUnchanged()

        with self.StaticMemberPatch():
            self.checkStaticMemberChangedTo('Static.member')

        self.checkStaticMemberUnchanged()

class PatchDecoratorFromFunctionTest(PatchTest):
    def testWithNewValue(self):
        from mocki.tools import Patch

        @self.StaticMemberPatch('newValue')
        def returnGivenArgsAndKwargs(*args, **kwargs):
            self.checkStaticMemberChangedTo('newValue')

            return (args, kwargs)

        self.checkStaticMemberUnchanged()

        self.assertEqual(returnGivenArgsAndKwargs('argValue', kwarg='kwargValue'),
                         (('argValue',), {'kwarg': 'kwargValue'}))

        self.checkStaticMemberUnchanged()

    def testWithNoNewValue(self):
        from mocki.tools import Patch

        @self.StaticMemberPatch()
        def returnGivenArgsAndKwargs(*args, **kwargs):
            self.checkStaticMemberChangedTo('Static.member')

            return (args, kwargs)

        self.checkStaticMemberUnchanged()

        self.assertEqual(returnGivenArgsAndKwargs('argValue', kwarg='kwargValue'),
                         (('argValue',), {'kwarg': 'kwargValue'}))

        self.checkStaticMemberUnchanged()

class PatchDecoratorFromMethodTest(PatchTest):
    def testWithNewValue(self):
        from mocki.tools import Patch

        selfTest = self

        class Test(object):
            @selfTest.StaticMemberPatch('newValue')
            def returnGivenArgsAndKwargs(self, *args, **kwargs):
                selfTest.checkStaticMemberChangedTo('newValue')

                return (args, kwargs)

        self.checkStaticMemberUnchanged()

        self.assertEqual(Test().returnGivenArgsAndKwargs('argValue', kwarg='kwargValue'),
                         (('argValue',), {'kwarg': 'kwargValue'}))

        self.checkStaticMemberUnchanged()

    def testWithNoNewValue(self):
        from mocki.tools import Patch

        selfTest = self

        class Test(object):
            @selfTest.StaticMemberPatch()
            def returnGivenArgsAndKwargs(self, *args, **kwargs):
                selfTest.checkStaticMemberChangedTo('Static.member')

                return (args, kwargs)

        self.checkStaticMemberUnchanged()

        self.assertEqual(Test().returnGivenArgsAndKwargs('argValue', kwarg='kwargValue'),
                         (('argValue',), {'kwarg': 'kwargValue'}))

        self.checkStaticMemberUnchanged()
