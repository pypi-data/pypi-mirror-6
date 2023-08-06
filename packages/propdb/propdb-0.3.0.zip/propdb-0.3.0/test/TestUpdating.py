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

class Test_TestUpdating(unittest.TestCase):
    """ Test all the update functionality. """

    def test_UpdateByFunction(self):
        """ Testing updating property items via the Set function. """

        bag = propbag(self._testMethodName, autosave = True)
        
        # Update item by propitem
        bag.add('item1')
        bag.set(propitem('item1', 111))
        item1 = bag['item1']
        self.assertIsNotNone(item1)
        self.assertEquals(item1.value, 111)
        
        # Update items by lists
        bag.add(('item2', 2, 'item3', 3))
        bag.set(('item2', 222, 'item3', 333))
        item2 = bag['item2']
        self.assertIsNotNone(item2)
        self.assertEquals(item2.value, 222)
        item3 = bag['item3']
        self.assertIsNotNone(item3)
        self.assertEquals(item3.value, 333)
        
        # Update items by dictionary
        bag.add({'item4':4, 'item5':5})
        bag.set({'item4':444, 'item5':555})
        item4 = bag['item4']
        self.assertIsNotNone(item4)
        self.assertEquals(item4.value, 444)
        item5 = bag['item5']
        self.assertIsNotNone(item5)
        self.assertEquals(item5.value, 555)
        
        # Try updating an item where the name is not a string
        bag.add('6')
        bag.set((6, 666))
        item6 = bag['6']
        self.assertIsNotNone(item6)
        self.assertNotEquals(item6.value, 666)
        self.assertEquals(item6.value, None)
           
        # Try updating by dictionary with names not as strings
        bag.add({'7':7, '8':8})
        bag.set({7:777, 8:888})
        item7 = bag['7']
        self.assertIsNotNone(item7)
        self.assertNotEquals(item7.value, 777)
        self.assertEquals(item7.value, 7)
        item8 = bag['8']
        self.assertIsNotNone(item8)
        self.assertNotEquals(item8.value, 888)
        self.assertEquals(item8.value, 8)

        delete_bag(bag)

    def test_UpdateByOperator(self):
        """ Testing updating property items via the [] operator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        # Update item with propitem by = operator
        bag.add('item1')
        bag['item1'] = propitem('item1', 111)
        item1 = bag['item1']
        self.assertIsNotNone(item1)
        self.assertEquals(item1.value, 111)
        
        # Update items with value by = operator
        bag.add(('item2', 2, 'item3', 3))
        bag['item2'] = 222
        bag['item3'] = 333
        item2 = bag['item2']
        self.assertIsNotNone(item2)
        self.assertEquals(item2.value, 222)
        item3 = bag['item3']
        self.assertIsNotNone(item3)
        self.assertEquals(item3.value, 333)
        
        # Try updating an item where the name is not a string
        bag.add('6')
        bag.set((6, 666))
        item6 = bag['6']
        self.assertIsNotNone(item6)
        self.assertNotEquals(item6.value, 666)
        self.assertEquals(item6.value, None)
           
        # Try updating by dictionary with names not as strings
        bag.add({'7':7, '8':8})
        bag.set({7:777, 8:888})
        item7 = bag['7']
        self.assertIsNotNone(item7)
        self.assertNotEquals(item7.value, 777)
        self.assertEquals(item7.value, 7)
        item8 = bag['8']
        self.assertIsNotNone(item8)
        self.assertNotEquals(item8.value, 888)
        self.assertEquals(item8.value, 8)

        delete_bag(bag)

if __name__ == '__main__':
    unittest.main()
