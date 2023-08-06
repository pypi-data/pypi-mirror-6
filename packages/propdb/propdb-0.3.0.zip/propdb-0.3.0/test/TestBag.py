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

class Test_TestBag(unittest.TestCase):
    """ Testing the general property functionality and properties. """

    def test_LenFunction(self):
        """ Tests if the len() function returns the correct count. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        self.assertEquals(len(bagItems) / 2, len(bag))

        delete_bag(bag)

    def test_ContainsAndIteratorFunction(self):
        """ Tests if the contains statement (in) returns the correct answer
        as well as the iterator. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        # test iterator
        for i in bag:
            # test 'in' with propitem
            self.assertTrue(i in bag)

            # test 'in' with name
            self.assertTrue(i.name in bag)

        delete_bag(bag)

    def test_IsDirtyAutosaveFunction(self):
        """ Tests if the is_dirty and autosave properties function properly. """

        bag = propbag(self._testMethodName, autosave = False)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        self.assertTrue(bag.is_dirty)

        bag.save()

        self.assertFalse(bag.is_dirty)

        bag.is_autosave = True

        bag.drop('item1')

        self.assertFalse(bag.is_dirty)

        bag.is_autosave = False

        bag.drop('item2')

        self.assertTrue(bag.is_dirty)

        delete_bag(bag)

    def test_NamesItemsFunction(self):
        """ Tests if the names and items properties work properly. """

        bag = propbag(self._testMethodName, autosave = True)
        
        bagItems = {'item1': 1, 'item2': 2, 'item3': 3, 'item4': 4 \
            , 'item5': 5, 'item6': 6, 'item7': 7, 'item8': 8}

        bag.add(bagItems)

        names = bag.names

        for name in names:
            self.assertTrue(name in bagItems)

        items = bag.items

        for i in items:
            self.assertTrue(i.name in bagItems)
            self.assertEquals(bagItems[i.name], i.value)

        delete_bag(bag)

    def test_LocationFunction(self):
        """ Tests if the location property returns the correct path. """

        folder = os.getcwd()

        bag = propbag(self._testMethodName, autosave = True)
        
        self.assertTrue(os.path.exists(bag.location))
        self.assertEquals(os.path.join(folder, self._testMethodName), bag.location)
        
        delete_bag(bag)

    def test_SaveFunction(self):
        """ Tests if saving actually writes to the file system. """

        bag = propbag(self._testMethodName, autosave = False)
        
        self.assertFalse(os.path.exists(bag.location))

        bag.save()

        self.assertTrue(os.path.exists(bag.location))
        
        delete_bag(bag)

if __name__ == '__main__':
    unittest.main()
