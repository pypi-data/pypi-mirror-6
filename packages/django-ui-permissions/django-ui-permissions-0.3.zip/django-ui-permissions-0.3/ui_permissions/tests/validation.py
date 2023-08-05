# -*- coding: utf-8 -*-

"""Module containing test for form validation."""

from django import forms
from django.utils import unittest

from ui_permissions.forms import UiPermFormMixin
from ui_permissions.descriptor.resource import (
    Resource,
    Field,
)


class EditableTestResource(Resource):

    """Tests all fields set to be editable."""

    name = Field.editable()
    age = Field.editable()


class HiddenTestResource(Resource):

    """Tests all fields set to be hidden."""

    name = Field.hidden()
    age = Field.hidden()


class TestForm(UiPermFormMixin, forms.Form):

    """Test form."""

    name = forms.CharField()
    age = forms.IntegerField(required=False)


class ValidationTestCase(unittest.TestCase):

    """Test form validation with given resource objects."""

    def test_editable(self):
        """Test editable form fields validation."""
        form = TestForm(data={}, resource_desc=EditableTestResource())
        self.assertFalse(form.is_valid())

        form = TestForm(data={'name': 'Test'}, resource_desc=EditableTestResource())
        self.assertTrue(form.is_valid())

    def test_excluded_fields(self):
        """Test excluded form fields validation."""
        form = TestForm(data={}, resource_desc=HiddenTestResource())
        self.assertTrue(form.is_valid())
