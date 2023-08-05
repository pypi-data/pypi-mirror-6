# -*- coding: utf-8 -*-

"""Module containing base for all component classes."""


class ComponentMeta(type):

    """Component meta class."""

    def __new__(cls, name, bases, attrs):
        for index, state_name in enumerate(attrs['states']):
            attrs[state_name] = index
        return super(ComponentMeta, cls).__new__(cls, name, bases, attrs)


class Component(object):

    """Component class."""

    __metaclass__ = ComponentMeta

    states = ()
    state_id = None

    def __init__(self, state_id):
        object.__setattr__(self, 'state_id', state_id)

    def __setattr__(self, name, value):
        raise AttributeError('Instance is immutable')

    def __delattr__(self, item):
        raise AttributeError('Instance is immutable')

    @property
    def state(self):
        """Name of the current component state."""
        return self.states[self.state_id]
