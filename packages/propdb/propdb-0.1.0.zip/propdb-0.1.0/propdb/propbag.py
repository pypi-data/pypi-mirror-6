#!/usr/bin/env python

import json
import os
import os.path
import threading

from propitem import propitem

class propbag(object):
    """ This class defines a property bag for storing property items. """

    def __init__(self, name, folder = None, autosave = False):
        ''' The bag initializer needs a name and folder location. '''

        self.__name = name

        if folder is None:
            self.__folder = os.getcwd()
        else:
            self.__folder = folder

        self.__autosave = autosave

        self.__is_dirty = False
        self.__suspend_autosave = False
        self.__lock = threading.RLock()
        self.__items = {}

        self.__init()

    def __add__(self, args):
        ''' Overloads the + operator. It is the same as calling the "add" method.
        
            Adding property items is very flexible. It is acceptable to add an item
            with just a name, a collection, or an instance of property item.

            propbag + 'item1' # adds a property item with the value set to None
            propbag + ('item1', 1, 'item2', 2, 'item3', 3, ...) # via tuple of name, value pairs
            propbag + ['item1', 1, 'item2', 2, 'item3', 3, ...] # via list of name, value pairs
            propbag + {'item1':1, 'item2':2, 'item3':3, ...} # via dictionary
            propbab + (propitem, propitem, ...)
            propbag + propitem

        '''

        self.add(args)

    def __iadd__(self, args):
        ''' Overloads the += operator. It is the same as calling the "add" method.
        
            Adding property items is very flexible. It is acceptable to add an item
            with just a name, a collection, or an instance of property item.

            propbag += 'item1' # adds a property item with the value set to None
            propbag += ('item1', 1, 'item2', 2, 'item3', 3, ...) # via tuple of name, value pairs
            propbag += ['item1', 1, 'item2', 2, 'item3', 3, ...] # via list of name, value pairs
            propbag += {'item1':1, 'item2':2, 'item3':3, ...} # via dictionary
            propbab += (propitem, propitem, ...)
            propbag += propitem

        '''

        self.add(args)

        return self

    def __sub__(self, args):
        ''' Overloads the - operator. It is the same as calling the "drop" method.
        
            Dropping property items is very flexible. It is acceptable to drop an item
            by name, a list of names, or an instance of property item.

            propbag - 'item1' # drops a property item by name as string
            propbag - ('item1', 'item2', 'item3', ...) # via tuple of names
            propbag - ['item1', 'item2', 'item3', ...] # via list of names
            propbab - (propitem, propitem, ...)
            propbag - propitem

        '''

        self.drop(args)

    def __isub__(self, args):
        ''' Overloads the - operator. It is the same as calling the "drop" method.
        
            Dropping property items is very flexible. It is acceptable to drop an item
            by name, a list of names, or an instance of property item.

            propbag -= 'item1' # drops a property item by name as string
            propbag -= ('item1', 'item2', 'item3', ...) # via tuple of names
            propbag -= ['item1', 'item2', 'item3', ...] # via list of names
            propbab -= (propitem, propitem, ...)
            propbag -= propitem

        '''

        self.drop(args)

        return self

    def __len__(self):
        ''' Overloads the len() method and returns the count of property items. '''

        return len(self.__items)

    def __getitem__(self, names):
        ''' Overloads the get [] operator and returns a copy of all the desired
       property items as a list. '''

        result = None

        if isinstance(names, basestring):
            if names in self.__items:
                result = self.__items[names].clone()
        elif isinstance(names, (list, tuple)):
            result = []
            for name in names:
                if name in self.__items:
                    result.append(self.__items[name].clone())

        return result

    def __setitem__(self, name, value):
        ''' Overloads the set [] operator. Name must be unique while
        the value can be anything but if it is a property item then 
        it is added directly and not wrapped by a property item class. '''

        if name in self.__items:
            if isinstance(value, propitem):
                self.__items[name].value = value.value
            else:
                self.__items[name].value = value

            self.__is_dirty = True

            if self.__autosave and not self.__suspend_autosave:
                self.__save()

    def __contains__(self, item):
        ''' Overloads the "in" operator. '''

        if isinstance(item, basestring):
            return item in self.__items
        elif isinstance(item, propitem):
            return item.name in self.__items

        return False

    def __iter__(self):
        ''' Allows iterating through a copy of the items in the property bag. '''

        for item in self.__items.viewvalues():
            yield item.clone()

    def __str__(self):
        ''' Returns a human-readable string of the property bag. '''

        return 'propbag [ Name: %s, Location: %s, Items: %s ]' \
            % (self.__name, self.__folder, len(self.__items))

    @property
    def is_dirty(self):
        ''' Returns True if one of the items in the property bag have
        changed since last saved. '''

        result = self.__is_dirty

        return result
    
    @property
    def is_autosave(self):
        ''' Gets the autosave feature setting. '''

        return self.__autosave

    @is_autosave.setter
    def is_autosave(self, value):
        ''' Sets the autosave feature setting. '''

        if isinstance(value, bool):
            self.__autosave = value

    @property
    def location(self):
        ''' Returns the location (full path file name) of the property bag. '''

        return os.path.join(self.__folder, self.__name)

    @property
    def names(self):
        ''' Returns a list of the names of each property item in the property bag.'''

        return self.__items.keys()

    @property
    def items(self):
        ''' Returns a copy of all the property items as a list. '''

        result = []

        for item in self.__items.itervalues():
            result.append(item.clone())

        return result

    def add(self, items):
        ''' Add property item(s) to the bag.
        
        Returns a list of all the added property items.
        
        Adding property items is very flexible. It is acceptable for "items"
        to be one or many. It can be just a name, a collection, or an
        instance of property item. Adding by list can be name/value pairs or
        a collection of property items. Adding by dictionary uses the key for
        the name and the value for the property item's value.

        Usage:
        # adds a property item with the value set to None
        propbag.add('item1')

        # by list of name/value pairs
        propbag.add(('item1', 1, 'item2', 2, ...))

        # by dictionary
        propbag.add({'item1':1, 'item2':2, ...})

        # by list or propitems
        propbag.add((propitem, propitem, ...))
        
        # by propitem
        propbag.add(propitem)

        Adding property items with the + and += operators can be done in the
        same exact way as the add method (e.g. propbag + propitem, etc). The
        only difference is that there is no return value when adding by
        operator.

        For example:
        propbag + 'item1'
        propbag += ('item1', 1, 'item2', 2, ...)
        
        '''

        result = []

        items_dict = {}

        # items is a string
        if isinstance(items, basestring):
            if items not in items_dict:
                items_dict[items] = None

        # items is a list
        elif isinstance(items, (list, tuple)):

            # is list an name/value pair or propitems
            isNameValuePair = False

            if len(items) > 0:
                if isinstance(items[0], basestring):
                    isNameValuePair = True

            if isNameValuePair:
                for i in range(0, len(items), 2):

                    if isinstance(items[i], basestring):
                        if items[i] not in items_dict:
                            # this item is a string so assume the next item
                            # is the value or will be set to None
                            if i + 1 < len(items):
                                items_dict[items[i]] = items[i + 1]
                            else:
                                items_dict[items[i]] = None

            else:
                for i in items:
                    if isinstance(i, propitem):
                        if i.name not in items_dict:
                            # this item is a propitem to add as name and value
                            items_dict[i.name] = i.value

        # items is a dictionary
        elif isinstance(items, dict):
            items_dict = items

        # items is a propitem
        elif isinstance(items, propitem):
            if items.name not in items_dict:
                items_dict[items.name] = items.value

        # add the parsed items that are now in items_dict
        for name, value in items_dict.iteritems():
            if name not in self.__items:
                item = propitem(name, value)
                self.__items[name] = item
                result.append(item.clone())
                self.__is_dirty = True

        if self.__autosave and not self.__suspend_autosave:
            self.__save()

        return result

    def drop(self, items):
        ''' Drop property item(s) from the bag.
        
        Returns the number of property items dropped.
        
        Dropping property items is very flexible. It is acceptable for
        "items" to be one or many as a single string, property item, or
        list.
            
        Passing a single string would be assumed as the name of a
        property item. Passing a list can either be a list of names or
        property items, mixed is acceptable as well
        (e.g. ('item1', propitem)).

        Usage:
        propbag.drop('item1') # drops one property by name
        propbag.drop(propitem) # drops one property item by name
        propbag.drop(('item1', 'item2', 'item3', ...)) # by list of names
        propbag.drop((propitem, propitem, ...)) # by list of propitems
        
        Dropping property items with the - and -= operators can be done in
        the same exact way as the drop method (e.g. propbag - propitem, etc).
        The only difference is that there is no return value when dropping
        by operator.

        For example:
        propbag - 'item1' # drops one property item by name
        propbag -= ('item1', 'item2', 'item3', ...) # via list of names

        '''

        result = 0;

        if isinstance(items, basestring):
            # drop by name if a string
            if items in self.__items:
                del self.__items[items]
                result += 1
                self.__is_dirty = True
        elif isinstance(items, (list, tuple)):
            # iterate collection and drop by name or propitem
            for i in items:
                if isinstance(i, basestring):
                    if i in self.__items:
                        del self.__items[i]
                        result += 1
                        self.__is_dirty = True
                elif isinstance(i, propitem):
                    if i.name in self.__items:
                        del self.__items[i.name]
                        result += 1
                        self.__is_dirty = True
        elif isinstance(items, propitem):
            # drop by propitem
            if items.name in self.__items:
                del self.__items[items.name]
                result += 1
                self.__is_dirty = True

        if self.__autosave and not self.__suspend_autosave:
            self.__save()

        return result

    def set(self, items):
        ''' Updates a property item(s) in the bag.
        
        Returns a list of all the updated property items.
        
        Updating property items is very flexible. It is acceptable for "items"
        to be one or many. It can be a collection or an instance of a
        property item. Updating by list must be by name/value pairs or a collection
        of property items. Updating by dictionary assumes the key to be
        the name and the dictionary value the value of the property item.

        Usage:

        # by list of name/value pairs
        propbag.set(('item1', 1, 'item2', 2, ...))

        # by dictionary
        propbag.set({'item1':1, 'item2':2, ...})

        # by list or propitems
        propbag.set((propitem, propitem, ...))
        
        # by propitem
        propbag.set(propitem)

        Updating property items with the [] operator can be done by
        indexing the property bag with the name of the property item
        and passing in a new value or a property item.

        For example:
        propbag['item1'] = value
        propbag[propitem.name] = propitem
        
        '''

        result = []

        items_dict = {}

        # items is a list
        if isinstance(items, (list, tuple)):

            # is list an name/value pair or propitems
            isNameValuePair = False

            if len(items) > 0:
                if isinstance(items[0], basestring):
                    isNameValuePair = True

            if isNameValuePair:
                for i in range(0, len(items), 2):

                    if isinstance(items[i], basestring):
                        if items[i] not in items_dict:
                            # this item is a string so assume the next item
                            # is the value. Ignore if no value
                            if i + 1 < len(items):
                                items_dict[items[i]] = items[i + 1]

            else:
                for i in items:
                    if isinstance(i, propitem):
                        if i.name not in items_dict:
                            # this item is a propitem to add as name and value
                            items_dict[i.name] = i.value

        # items is a dictionary
        elif isinstance(items, dict):
            items_dict = items

        # items is a propitem
        elif isinstance(items, propitem):
            if items.name not in items_dict:
                items_dict[items.name] = items.value

        # add the parsed items that are now in items_dict
        for name, value in items_dict.iteritems():
            if name in self.__items:
                self.__items[name].value = value
                result.append(self.__items[name].clone())
                self.__is_dirty = True

        if self.__autosave and not self.__suspend_autosave:
            self.__save()

        return result

    def save(self):
        ''' Saves the property bag. '''

        if self.is_dirty:
            if self.__save() != len(self.__items):
                raise IOError('Failed to save all the items.')

    def suspend_autosave(self):
        ''' Suspends the autosave feature. Use when changing multiple property items while
        autosave feature is activated. Forcing a save, even while suspended, is possible by
        calling the save method. '''

        self.__suspend_autosave = True

    def resume_autosave(self):
        ''' Resumes automatically saving when the autosave feature is activated.
        If the bag is dirty and the autosave feature is enabled then the bag
        will be saved. '''

        self.__suspend_autosave = False

        if self.__autosave:
            self.save()

    def __init(self):
        ''' Internal iniatizer that either creates or loads the property bag. '''

        if os.path.exists(os.path.join(self.__folder, self.__name)):
            with open(os.path.join(self.__folder, self.__name), 'r') as f:
                contents = json.load(f)

                for name, value in contents.iteritems():
                    if isinstance(name, basestring) and name not in self.__items:
                        self.__items[name] = propitem(name, value)
        else:
            # marking as dirty because it is new and if autosave is false then the
            # property bag will not be saved until save() is called
            self.__is_dirty = True
            if self.__autosave:
                self.save()

    def __save(self):
        ''' Saves the items dictionary to the file system as a serialized JSON object. '''

        with self.__lock:
            # build a JSON serializable dictionary from items
            contents = {}
            for name, value in self.__items.iteritems():
                contents[name] = value.value

            # dump dictionary to file
            with open(os.path.join(self.__folder, self.__name), 'w') as f:
                f.write(json.dumps(contents))

            # mark bag as clean
            self.__is_dirty = False

        # return number of items saved
        return len(contents)
        

