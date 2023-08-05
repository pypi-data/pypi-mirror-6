# Copyright (c) 2012 by Enthought Inc.

import time
import unittest

from enaml.application import deferred_call
from traits.api import Float, HasTraits, Int, List, on_trait_change

from ..gui_test_assistant import GuiTestAssistant


class MyClass(HasTraits):

    number = Float(2.0)
    list_of_numbers = List(Float)

    @on_trait_change('number')
    def _add_number_to_list(self, value):
        self.list_of_numbers.append(value)

    def add_to_number(self, value):
        self.number += value


class EventLoopUser(HasTraits):

    value = Int(0)

    maximum_value = Int(15)

    def increase_value(self):
        time.sleep(0.01)
        self.value += 1
        if self.value < self.maximum_value:
            deferred_call(self.increase_value)


class TestGuiAssistantTestCase(GuiTestAssistant, unittest.TestCase):

    def setUp(self):
        self.my_class = MyClass()
        GuiTestAssistant.setUp(self)

    def _set_trait(self, value):
        self.my_class.number = value

    def test_trait_change_on_event_loop(self):
        condition = lambda obj: obj.number == 5.0
        with self.assertTraitChangesInEventLoop(
                self.my_class, 'number', condition) as collector:
            deferred_call(self._set_trait, 5.0)
        self.assertEqual(collector.event_count, 1)

    def test_timeout(self):
        condition = lambda obj: obj.number == 3.0
        with self.assertRaises(AssertionError):
            with self.assertTraitChangesInEventLoop(
                    self.my_class, 'number', condition, timeout=0.5):
                deferred_call(self._set_trait, 2.0)

    def test_exception_in_context(self):
        condition = lambda obj: True
        with self.assertRaises(RuntimeError):
            with self.assertTraitChangesInEventLoop(
                    self.my_class, 'number', condition):
                raise RuntimeError()

    def test_event_loop_until_condition(self):
        obj = EventLoopUser()
        condition = lambda: obj.value == obj.maximum_value
        with self.event_loop_until_condition(condition, timeout=2.0):
            deferred_call(obj.increase_value)

    def test_event_loop_until_condition_timeout(self):
        obj = EventLoopUser(value=10, maximum_value=1)
        condition = lambda: obj.value == obj.maximum_value
        with self.assertRaises(AssertionError):
            with self.event_loop_until_condition(condition, timeout=0.5):
                deferred_call(obj.increase_value)

    def test_event_loop_until_condition_exception(self):
        obj = EventLoopUser()
        condition = lambda: obj.value == obj.maximum_value
        with self.assertRaises(RuntimeError):
            with self.event_loop_until_condition(condition, timeout=1.0):
                raise RuntimeError()
