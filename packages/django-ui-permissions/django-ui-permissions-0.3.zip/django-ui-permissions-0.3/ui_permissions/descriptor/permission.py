# -*- coding: utf-8 -*-

"""Module containing Permission class."""

from .resource import Resource, ResourceSet


class Permission(object):

    @classmethod
    def get_resource(cls, url_name):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            try:
                if issubclass(attr, Resource) and url_name in attr._Settings.url:
                    return attr
            except TypeError:
                pass

    @classmethod
    def get_referenced_resources(cls, reference_target):
        """Get all resource objects that point to reference_target.

        :param reference_target: reference target class
        :type reference_target: ui_permissions.descriptor.resource.Resource
        :returns: grouped resource instances
        :rtype: ui_permissions.descriptor.resource.ResourceSet

        """
        resource_set = None
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            try:
                if issubclass(attr, Resource) and \
                                attr._Settings.bind_reference_name is not None and \
                                attr._Settings.bind_reference_name == reference_target.__name__:
                    if resource_set is None:
                        resource_set = ResourceSet()
                    resource_set.add(attr)
            except TypeError:
                pass
        return resource_set
