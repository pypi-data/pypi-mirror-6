# -*- coding: utf-8 -*-

"""Module containing components tests."""

from django.utils import unittest

from ui_permissions.descriptor.components import Element, Field


class ElementTestCase(unittest.TestCase):

    """Test for checking proper Element class initialization."""

    def test_states_presence(self):
        """Check if class has all declared states."""
        for state_name in Element.states:
            self.assertTrue(hasattr(Element, state_name), state_name)

    def test_object_immutability(self):
        """Check if instance is immutable."""
        element_obj = Element.visible()

        setattr_test = lambda obj, attr_name: setattr(obj, attr_name, None)
        self.assertRaises(AttributeError, setattr_test, element_obj, 'state_id')
        self.assertRaises(AttributeError, setattr_test, element_obj, 'states')
        self.assertRaises(AttributeError, setattr_test, element_obj, 'state')
        self.assertRaises(AttributeError, setattr_test, element_obj, 'VISIBLE')
        self.assertRaises(AttributeError, setattr_test, element_obj, 'HIDDEN')

        delattr_test = lambda obj, attr_name: delattr(obj, attr_name)
        self.assertRaises(AttributeError, delattr_test, element_obj, 'state_id')
        self.assertRaises(AttributeError, delattr_test, element_obj, 'states')
        self.assertRaises(AttributeError, delattr_test, element_obj, 'state')
        self.assertRaises(AttributeError, delattr_test, element_obj, 'VISIBLE')
        self.assertRaises(AttributeError, delattr_test, element_obj, 'HIDDEN')


class FieldTestCase(unittest.TestCase):

    """Test for checking proper Field class initialization."""

    def test_states_presence(self):
        """Check if class has all declared states."""
        for state_name in Field.states:
            self.assertTrue(hasattr(Field, state_name), state_name)

    def test_object_immutability(self):
        """Check if instance is immutable."""
        field_obj = Field.editable()

        setattr_test = lambda obj, attr_name: setattr(obj, attr_name, None)
        self.assertRaises(AttributeError, setattr_test, field_obj, 'state_id')
        self.assertRaises(AttributeError, setattr_test, field_obj, 'states')
        self.assertRaises(AttributeError, setattr_test, field_obj, 'state')
        self.assertRaises(AttributeError, setattr_test, field_obj, 'EDITABLE')
        self.assertRaises(AttributeError, setattr_test, field_obj, 'DISABLED')
        self.assertRaises(AttributeError, setattr_test, field_obj, 'HIDDEN')

        delattr_test = lambda obj, attr_name: delattr(obj, attr_name)
        self.assertRaises(AttributeError, delattr_test, field_obj, 'state_id')
        self.assertRaises(AttributeError, delattr_test, field_obj, 'states')
        self.assertRaises(AttributeError, delattr_test, field_obj, 'state')
        self.assertRaises(AttributeError, delattr_test, field_obj, 'EDITABLE')
        self.assertRaises(AttributeError, delattr_test, field_obj, 'DISABLED')
        self.assertRaises(AttributeError, delattr_test, field_obj, 'HIDDEN')
