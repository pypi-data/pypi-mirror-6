# -*- coding: utf-8 -*-

"""Module containing views mixins."""

from django.http import Http404
from django.core.urlresolvers import resolve


class UiPermViewMixin(object):

    """Base class for other view mixins."""

    def get_perm_desc(self, request, *args, **kwargs):
        """Get permissions class for given user in request.

        This method must be overridden. Returning None means that request for given URL(resource) is blocked.

        :param request: HTTP request
        :type request: django.http.HttpRequest
        :returns: class that inherits from ui_permissions.descriptor.permission.Permission or None
        :rtype: class or None

        """
        raise NotImplementedError()

    def handle_refusal(self, permission=None, resource=None):
        """Fired when view determines that given request is not allowed to proceed.

        If permission and resource are None no permission class was found.
        If resource is None then it means that user is not allowed to see this resource.
        If permission and resource are not None resource method is_owner returned False.

        :param permission: permission description class
        :type permission: class
        :param resource: resource description class
        :type resource: class
        :returns: Http response
        :rtype: django.http.response.HttpResponse

        """
        raise Http404()

    def dispatch(self, request, *args, **kwargs):
        permission_class = self.get_perm_desc(request, *args, **kwargs)
        if permission_class is None:
            return self.handle_refusal()

        resource_class = permission_class.get_resource(resolve(request.path_info).url_name)
        if resource_class is None:
            return self.handle_refusal(permission_class)
        if not resource_class.is_owner(request, kwargs):
            return self.handle_refusal(permission_class, resource_class)

        self.resource_desc = resource_class()

        resource_set = permission_class.get_referenced_resources(resource_class)
        if resource_set is not None:
            self.resource_set = resource_set

        return super(UiPermViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UiPermViewMixin, self).get_context_data(**kwargs)
        context['resource_desc'] = self.resource_desc
        if hasattr(self, 'resource_set'):
            context['resource_set'] = self.resource_set
        return context


class UiPermFormViewMixin(UiPermViewMixin):

    """Mixin used with Django built-in forms views."""

    def get_form_kwargs(self):
        kwargs = super(UiPermFormViewMixin, self).get_form_kwargs()
        kwargs['resource_desc'] = self.resource_desc
        return kwargs
