#!/usr/bin/env python

import copy
import time

class actiontype:
    none, add, set, drop = range(4)

    @staticmethod
    def is_supported(value):
        """ Returns true of the action type is supported. """

        if value == actiontype.add or value == actiontype.set \
            or value == actiontype.drop or value == actiontype.none:
            return True
        else:
            return result

class propitem(object):
    """ This container class defines a property item that is stored in a property bag. """

    def __init__(self, n, v = None):
        """ The class initializer takes the item a name and an optional value.
        The name must be unique to the property bag. """

        if not isinstance(n, basestring):
            raise TypeError('Name must be of string type.')

        self.__name = n
        self.__value = v
        self.__timestamp = time.time()
        self.__is_dirty = True
        self.__action_type = actiontype.none

    def __str__(self):
        """ Returns a human-readable string of the property item. """

        return 'propitem [ Name: %s, ValueType: %s ]' % (self.__name, type(self.__value))

    @property
    def name(self):
        """ Gets the name of the property item. """

        return self.__name

    @property
    def value(self):
        """ Gets the value of the property item. """

        return self.__value

    @value.setter
    def value(self, v):
        """ Sets the value of the property item. """

        if self.__value != v:
            self.__value = v
            self.__timestamp = time.time()
            self.__is_dirty = True

    @property
    def timestamp(self):
        """ Gets the last modified timestamp. """

        return self.__timestamp

    @property
    def is_dirty(self):
        """ Returns True if the item has been modified since last saved. """

        return self.__is_dirty

    @is_dirty.setter
    def is_dirty(self, v):
        """ Set the is_dirty property. """

        if self.__is_dirty != v:
            self.__is_dirty = v

    @property
    def action_type(self):
        """ Gets the action_type property. """

        return self.__action_type

    @action_type.setter
    def action_type(self, v):
        """ Sets the action_type property. """

        if self.__action_type != v:
            self.__action_type = v

    def clone(self):
        """ Creates a copy of this property item. """

        return propitem(self.__name, copy.copy(self.__value))