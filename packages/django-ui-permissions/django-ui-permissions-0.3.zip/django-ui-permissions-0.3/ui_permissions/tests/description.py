# -*- coding: utf-8 -*-

"""Module containing test permission description."""

from django.utils import unittest

from ui_permissions.descriptor.components import Element, Field
from ui_permissions.descriptor.resource import (
    Resource,
    url,
    default_if_not_present,
    bind_to,
)
from ui_permissions.descriptor.permission import Permission


class BaseTestPermission(Permission):
    @url('test')
    @default_if_not_present(element=Element.HIDDEN, field=Field.DISABLED)
    class TestResource(Resource):
        pass


class Test1Permission(BaseTestPermission):
    pass


class Test2Permission(BaseTestPermission):
    @url('other_test')
    class TestResource(BaseTestPermission.TestResource):
        pass


class Test3Permission(BaseTestPermission):
    @default_if_not_present(field=Field.HIDDEN)
    class TestResource(BaseTestPermission.TestResource):
        pass


class PermissionTestCase(unittest.TestCase):

    """Tests Permission behaviour."""

    def _check(self, permission_cls, urls, defaults):
        """Check if proper resource was returned and if it has correct default states set."""
        for url_name in urls:
            resource_cls = permission_cls.get_resource(url_name)
            self.assertEquals(resource_cls, urls[url_name], url_name)

            if resource_cls is not None:
                resource = resource_cls()
                self.assertTrue(getattr(resource.element.ghost_element, defaults['element']))
                self.assertTrue(getattr(resource.field.ghost_field, defaults['field']))

    def test_description(self):
        """Check if description mechanism works properly."""
        self._check(Test1Permission,
                    {'test': Test1Permission.TestResource, 'other_test': None},
                    {'element': 'HIDDEN', 'field': 'DISABLED'})

        self._check(Test2Permission,
                    {'other_test': Test2Permission.TestResource, 'test': None},
                    {'element': 'HIDDEN', 'field': 'DISABLED'})

        self._check(Test3Permission,
                    {'test': Test3Permission.TestResource, 'other_test': None},
                    {'element': 'HIDDEN', 'field': 'HIDDEN'})


class BindTestPermission(Permission):
    @url('main')
    class MainResource(Resource):
        pass

    @url('sub_main')
    @bind_to('MainResource', bind_name='accessible_sub_resource')
    class AccessibleSubResource(Resource):
        pass

    @bind_to('MainResource')
    class SubResource(Resource):
        pass

    @url('another')
    class AnotherResource(Resource):
        pass


class BindTestCase(unittest.TestCase):

    """Test binding mechanism in permission description."""

    def test_reference_collecting(self):
        """Check if all references to main resource has been found."""
        resource_cls = BindTestPermission.get_resource('main')
        resource_set = BindTestPermission.get_referenced_resources(resource_cls)
        self.assertIsNotNone(resource_set)
        self.assertTrue(hasattr(resource_set, 'accessible_sub_resource'))
        self.assertTrue(hasattr(resource_set, 'subresource'))
        self.assertFalse(hasattr(resource_set, 'anotherresource'))

    def test_not_reference_resource(self):
        """Check referenced resource collecting for non referenced resource."""
        resource_cls = BindTestPermission.get_resource('another')
        resource_set = BindTestPermission.get_referenced_resources(resource_cls)
        self.assertIsNone(resource_set)

    def test_query_on_collected_resources(self):
        """Check if querying mechanism works on collected resources."""
        resource_cls = BindTestPermission.get_resource('main')
        resource_set = BindTestPermission.get_referenced_resources(resource_cls)
        self.assertTrue(resource_set.accessible_sub_resource.field.test_field.EDITABLE)
        self.assertFalse(resource_set.accessible_sub_resource.field.test_field.DISABLED)
        self.assertFalse(resource_set.accessible_sub_resource.field.test_field.HIDDEN)

        self.assertTrue(resource_set.subresource.element.test_field.VISIBLE)
        self.assertFalse(resource_set.subresource.element.test_field.HIDDEN)
