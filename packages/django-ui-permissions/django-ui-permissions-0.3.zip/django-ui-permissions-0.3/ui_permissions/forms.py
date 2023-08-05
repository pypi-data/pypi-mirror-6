# -*- coding: utf-8 -*-

"""Module containing forms mixins."""

from ui_permissions.descriptor.resource import Resource


class UiPermFormMixin(object):

    """Mixin that allows passing extra keyword argument into form class constructor."""

    def __init__(self, **kwargs):
        self.resource_desc = kwargs.pop('resource_desc', Resource())
        super(UiPermFormMixin, self).__init__(**kwargs)

    def _clean_fields(self):
        excluded_fields = self.resource_desc.get_excluded_fields(self.fields.keys())
        modified_fields = []
        # Temporally change all required fields to non required.
        for name, field in self.fields.items():
            if name in excluded_fields and field.required:
                field.required = False
                modified_fields.append(name)

        super(UiPermFormMixin, self)._clean_fields()

        # Revert changes after each field has been cleaned.
        for name in modified_fields:
            self.fields[name].required = True


class UiPermModelFormMixin(UiPermFormMixin):

    """Mixin used with model form classes."""

    def _clean_form(self):
        for field_name in self.resource_desc.get_excluded_fields(self.fields.keys()):
            if hasattr(self.instance, field_name):
                self.cleaned_data[field_name] = getattr(self.instance, field_name)
        super(UiPermModelFormMixin, self)._clean_form()

    def _get_validation_exclusions(self):
        exclude = super(UiPermModelFormMixin, self)._get_validation_exclusions()
        exclude.extend(self.resource_desc.get_excluded_fields(self.fields.keys()))
        return list(set(exclude))
