import unittest
import os
import os.path

from propdb.propbag import propbag
from propdb.propbag import propitem

def delete_bag(bag):
    """ Deletes a propbag. """

    if isinstance(bag, propbag):
        if bag is not None and os.path.exists(bag.location):
            os.remove(bag.location)

class Test_TestDeleting(unittest.TestCase):
    """ Test all the delete functionality. """

    def test_DeleteByFunction(self):
        """ Testing deleting property items via the Drop function. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Drop item with just a name
        bag.drop('item1')
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop items by lists
        bag.drop(('item2', 'item3'))
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        bag.drop(['item4', 'item5'])
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop item as propitem
        bag.drop(propitem('item6'))
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop mixed items in list
        bag.drop(['item7', propitem('item8')])
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Try deleting an item where the name is not a string
        bag.drop(1)
        self.assertEquals(len(bag), bagItemCount)
        
        # Try deleting by list with names not as strings
        bag.drop((10, 11, 12, 13))
        self.assertEquals(len(bag), bagItemCount)
        
        # Empty bag
        bag.drop(bagItems)
        self.assertEquals(len(bag), 0)

        delete_bag(bag)

    def test_DeleteByOperator(self):
        """ Testing deleting property items via the - (subtract) operator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Drop item with just a name
        bag - 'item1'
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop items by lists
        bag - ('item2', 'item3')
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        bag - ['item4', 'item5']
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop item as propitem
        bag - propitem('item6')
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop mixed items in list
        bag - ['item7', propitem('item8')]
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Try deleting an item where the name is not a string
        bag - 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Try deleting by list with names not as strings
        bag - (10, 11, 12, 13)
        self.assertEquals(len(bag), bagItemCount)
        
        # Empty bag
        bag - bagItems
        self.assertEquals(len(bag), 0)

        delete_bag(bag)

    def test_DeleteByOperator(self):
        """ Testing deleting property items via the -= (subtract equals) operator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Drop item with just a name
        bag -= 'item1'
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop items by lists
        bag -= ('item2', 'item3')
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        bag -= ['item4', 'item5']
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop item as propitem
        bag -= propitem('item6')
        bagItemCount -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Drop mixed items in list
        bag -= ['item7', propitem('item8')]
        bagItemCount -= 2
        self.assertEquals(len(bag), bagItemCount)

        # load bag
        bag.add(bagItems)

        bagItemCount = len(bag)

        # Try deleting an item where the name is not a string
        bag -= 1
        self.assertEquals(len(bag), bagItemCount)
        
        # Try deleting by list with names not as strings
        bag -= (10, 11, 12, 13)
        self.assertEquals(len(bag), bagItemCount)
        
        # Empty bag
        bag -= bagItems
        self.assertEquals(len(bag), 0)

        delete_bag(bag)

if __name__ == '__main__':
    unittest.main()
