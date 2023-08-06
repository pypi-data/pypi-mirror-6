#!/usr/bin/env python

import copy

class propitem(object):
    """ This container class defines a property item that is stored in a property bag. """

    def __init__(self, name, value = None):
        ''' The class initializer takes the item a name and an optional value.
        The name must be unique to the property bag. '''

        self.__name = name
        self.__value = value

    def __str__(self):
        ''' Returns a human-readable string of the property item. '''

        return 'propitem [ Name: %s, ValueType: %s ]' % (self.__name, type(self.__value))

    @property
    def name(self):
        ''' Gets the name of the property item. '''

        return self.__name

    @property
    def value(self):
        ''' Gets the value of the property item. '''

        return self.__value

    @value.setter
    def value(self, value):
        ''' Sets the value of the property item. '''

        if (self.__value != value):
            self.__value = value

    def clone(self):
        ''' Creates a copy of this property item. '''

        return propitem(self.__name, copy.copy(self.__value))