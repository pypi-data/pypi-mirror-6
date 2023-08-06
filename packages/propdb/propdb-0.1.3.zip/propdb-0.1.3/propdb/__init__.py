#!/usr/bin/env python

''' Property bag style database package

The propbd package is a simple database module. It is basically a
persisting Python dictionary.

Property item name's are dictionary keys and the dictionary values are
property items. The keys are enforced to be of basestring type whereas
the values can be anything, almost. The property bag is saved to the file
system by serializing the dictionary as JSON; therefore, the property
item values must be able to be seriailized by the json module.

Property bag name and location form the path where the bag is saved. If no
location is set then the current working directory is used. Property bags
are created by instantiating a propbag. Property items are created by
calling add from the bag instance.

If autosave is true then the bag will automatically save when property
items are added, updated, or dropped. If multiple items need to be added,
updated, or dropped then suspend autosave before operations
by calling suspend_autosave(). Resume autosaving once operations are
completed by calling resume_autosave(). If autosave is false then the bag
can manually be saved by calling the save() method. Checking the is_dirty
property on the bag indicates if the bag needs to be saved.

Property items in a property bag can be iterated directly on the instance
of the bag (e.g. for item in bag).

Basic usage of propdb is shown below.

from propdb import propbag as bag
from propdb import propitem as item

# create a new property bag
b1 = bag('bag1', autosave = True)

# suspend saving until all items have been added
b1.suspend_autosave()
i1 = b1.add(('item1', 1))
i2 = b1.add(('item2', [2, 2]))
i3 = b1.add(('item3', {'1':1, '2':2, '3':3}))
b1.resume_autosave()
    
# print name/value pairs by iterating over the property bag
for item in b1:
    print('%s=%s' % (item.name, item.value))

# add a new item
b1.add('item4')

# get that new item and update it
i4 = b1['item4']
if i4 != None:
    i4.value = '4'
    b1.set(i4)

# get all the names of the property items in the property bag
print('names: %s' % b1.names)

# get all the items
print('values: %s' % b1.items)

# get many property items via list of names. a list is returned.
i1and2 = b1[('item1', 'item2')]

# turn autosave off
b1.is_autosave = False

# create two new itmes via a dict of name:value
b1.add({'item5':5, 'item6':6})

# bag is dirty
print('dirty: %s' % b1.is_dirty)

# save bag
b1.save()

# bag is clean
print('dirty: %s' % b1.is_dirty)

# turn autosave on
b1.is_autosave = True

# drop one item
b1.drop('item6')

# drop many items
b1.drop(('item5', 'item4'))

for item in b1:
    print('%s=%s' % (item.name, item.value))

'''

__author__ = 'Dax Wilson'
__copyright__ = 'Copyright 2014. All rights reserved.'
__credits__ = []

__license__ = 'GNU-GPL'
__version__ = '0.1.3'
__maintainer__ = 'Dax Wilson'
__email__ = 'daxwilson@gmail.com'
__status__ = 'Development'

#from propbag import propbag as bag
#from propitem import propitem as item

if __name__ == '__main__':
    
    pass

    ## create a new property bag
    #b1 = bag('bag1', autosave = True)

    ## suspend saving until all items have been added
    #b1.suspend_autosave()
    #i1 = b1.add(('item1', 1))
    #i2 = b1.add(('item2', [2, 2]))
    #i3 = b1.add(('item3', {'1':1, '2':2, '3':3}))
    #b1.resume_autosave()
    
    ## print name/value pairs by iterating over the property bag
    #for item in b1:
    #    print('%s=%s' % (item.name, item.value))

    ## add a new item
    #b1.add('item4')

    ## get that new item and update it
    #i4 = b1['item4']
    #if i4 != None:
    #    i4.value = '4'
    #    b1.set(i4)

    ## get all the names of the property items in the property bag
    #print('names: %s' % b1.names)

    ## get all the items
    #print('values: %s' % b1.items)

    ## get many property items via list of names. a list is returned.
    #i1and2 = b1[('item1', 'item2')]

    ## turn autosave off
    #b1.is_autosave = False

    ## create two new itmes via a dict of name:value
    #b1.add({'item5':5, 'item6':6})

    ## bag is dirty
    #print('dirty: %s' % b1.is_dirty)

    ## save bag
    #b1.save()

    ## bag is clean
    #print('dirty: %s' % b1.is_dirty)

    ## turn autosave on
    #b1.is_autosave = True

    ## drop one item
    #b1.drop('item6')

    ## drop many items
    #b1.drop(('item5', 'item4'))

    #for item in b1:
    #    print('%s=%s' % (item.name, item.value))