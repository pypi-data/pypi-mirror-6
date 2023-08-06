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

class Test_TestAdding(unittest.TestCase):
    """ Test all the add functionality. """

    def test_AddByFunction(self):
        """ Testing adding property items via the Add function. """

        bag = propbag(self._testMethodName, autosave = True)
        
        # Add item with just a name
        item1 = bag.add('item1')
        self.assertIsNotNone(item1[0])
        self.assertEqual(item1[0].name, 'item1')
        self.assertIsNone(item1[0].value)
        self.assertEquals(len(bag), 1)
        
        # Add items by lists
        items23 = bag.add(('item2', 2, 'item3', 3))
        self.assertEquals(len(items23), 2)
        items45 = bag.add(['item4', 4, 'item5', 5])
        self.assertEquals(len(items45), 2)
        self.assertEquals(len(bag), 5)
        
        # Add item as propitem
        item6 = propitem('item6', 6)
        bag.add(item6)
        self.assertEquals(len(bag), 6)
        
        # Add items by dictionary
        bag.add({'item7':7, 'item8':8})
        self.assertEquals(len(bag), 8)
        
        # Try adding an item where the name is not a string
        bag.add(9)
        self.assertEquals(len(bag), 8)
        
        # Try adding by list with names not as strings
        bag.add((10, 11, 12, 13))
        self.assertEquals(len(bag), 8)
           
        # Try adding by dictionary with names not as strings
        bag.add({14:15, 16:17})
        self.assertEquals(len(bag), 8)

        # Try adding by list with one name not a string
        items1819 = bag.add(['item18', 18, 19, 19])
        self.assertEquals(len(items1819), 1)
        self.assertEquals(len(bag), 9)

        # Try adding by dictionary with one name not a string
        items2021 = bag.add({'item20':20, 21:21})
        self.assertEquals(len(items2021), 1)
        self.assertEquals(len(bag), 10)

        delete_bag(bag)

    def test_AddByOperator(self):
        """ Testing adding property items via the + (add) operator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        # Add item with just a name
        bag + 'item1'
        self.assertEquals(len(bag), 1)
        
        # Add items by lists
        bag + ('item2', 2, 'item3', 3)
        bag + ['item4', 4, 'item5', 5]
        self.assertEquals(len(bag), 5)
        
        # Add item as propitem
        item6 = propitem('item6', 6)
        bag + item6
        self.assertEquals(len(bag), 6)
        
        # Add items by dictionary
        bag + {'item7':7, 'item8':8}
        self.assertEquals(len(bag), 8)
        
        # Try adding an item where the name is not a string
        bag + 9
        self.assertEquals(len(bag), 8)
        
        # Try adding by list with names not as strings
        bag + (10, 11, 12, 13)
        self.assertEquals(len(bag), 8)
           
        # Try adding by dictionary with names not as strings
        bag + {14:15, 16:17}
        self.assertEquals(len(bag), 8)

        # Try adding by list with one name not a string
        bag + ['item18', 18, 19, 19]
        self.assertEquals(len(bag), 9)

        # Try adding by dictionary with one name not a string
        bag + {'item20':20, 21:21}
        self.assertEquals(len(bag), 10)

        delete_bag(bag)

    def test_AddEqualByOperator(self):
        """ Testing adding property items via the += (add equal) operator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        # Add item with just a name
        bag += 'item1'
        self.assertEquals(len(bag), 1)
        
        # Add items by lists
        bag += ('item2', 2, 'item3', 3)
        bag += ['item4', 4, 'item5', 5]
        self.assertEquals(len(bag), 5)
        
        # Add item as propitem
        item6 = propitem('item6', 6)
        bag += item6
        self.assertEquals(len(bag), 6)
        
        # Add items by dictionary
        bag += {'item7':7, 'item8':8}
        self.assertEquals(len(bag), 8)
        
        # Try adding an item where the name is not a string
        bag += 9
        self.assertEquals(len(bag), 8)
        
        # Try adding by list with names not as strings
        bag += (10, 11, 12, 13)
        self.assertEquals(len(bag), 8)
           
        # Try adding by dictionary with names not as strings
        bag += {14:15, 16:17}
        self.assertEquals(len(bag), 8)

        # Try adding by list with one name not a string
        bag += ['item18', 18, 19, 19]
        self.assertEquals(len(bag), 9)

        # Try adding by dictionary with one name not a string
        bag += {'item20':20, 21:21}
        self.assertEquals(len(bag), 10)

        delete_bag(bag)

if __name__ == '__main__':
    unittest.main()
