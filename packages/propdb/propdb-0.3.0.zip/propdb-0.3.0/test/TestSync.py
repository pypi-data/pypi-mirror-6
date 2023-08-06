import unittest
import os
import os.path
import time

from propdb.propbag import propbag
from propdb.propbag import propitem

def delete_bag(bag):
    """ Deletes a propbag. """

    if isinstance(bag, propbag):
        if bag is not None and os.path.exists(bag.location):
            os.remove(bag.location)

class Test_TestSync(unittest.TestCase):

    def test_SyncFunction(self):
        
        bag1 = propbag(self._testMethodName, autosave = False)
        bag2 = propbag(self._testMethodName, autosave = False)

        # test adding items that were not present in other instances
        bag1.add(('a', 1))
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertTrue('a' in bag2)

        # test updating items that are not marked as changed
        bag1.set({'a': 2})
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertTrue(bag2['a'].value == 2)

        # test dropping items that are not marked as changed
        bag1.drop('a')
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertFalse('a' in bag2)
        
        # test dropping
        """
         when dropping...
	        if exists...
		        if timestamp <=, do not delete (aka add it back to the bag)
		        if newer, do nothing, leave it deleted
	        if does not exist...
		        do nothing, leave it deleted
        """
        bag1.add(('b', 1))
        bag1.save()
        time.sleep(1)
        bag2.sync()
        time.sleep(1)
        bag2 - 'b'
        self.assertFalse('b' in bag2)
        time.sleep(1)
        bag1['b'] = 2
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertTrue('b' in bag2)
        self.assertTrue(bag2['b'].value == 2)
        time.sleep(1)
        bag2 - 'b'
        time.sleep(1)
        bag2.sync()
        self.assertFalse('b' in bag2)
        bag2 + ('c', 1)
        self.assertTrue('c' in bag2)
        bag2 - 'c'
        self.assertFalse('c' in bag2)
        bag2.sync()
        self.assertFalse('c' in bag2)
        time.sleep(1)

        # test adding
        """
         when adding...
	        if already exists...
		        if timestamp <=, update this instance value
		        if newer, do nothing, value is the latest
	        if does not exist...
		        do nothing, value is the latest
        """
        bag1 + ('d', 1)
        bag2 + ('d', 2)
        bag1['d'] = 3
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertTrue(bag2['d'].value == 3)
        time.sleep(1)
        bag2['d'] = 4
        time.sleep(1)
        bag2.sync()
        self.assertTrue(bag2['d'].value == 4)
        bag2 + ('e', 1)
        bag2.sync()
        self.assertTrue(bag2['e'].value == 1)

        # test updating
        """
        when updating...
	        if exists...
		        if timestamp <=, update from file
		        if newer, do nothing, value is latest
	        if does not exist...
		        if timestamp <=, delete from this instance
                if newer, do nothing, value is latest
        """
        bag1.add('a')
        bag1.save()
        time.sleep(1)
        bag2.sync()
        bag2['a'] = 9
        time.sleep(1)
        bag1['a'] = 10
        bag1.save()
        bag2.sync()
        self.assertTrue(bag2['a'].value == 10)
        bag1['a'] = 11
        bag1.save()
        time.sleep(1)
        bag2['a'] = 20
        bag2.sync()
        self.assertTrue(bag2['a'].value == 20)
        bag1 - 'a'
        bag1.save()
        time.sleep(1)
        bag2.sync()
        self.assertFalse('a' in bag2)
        time.sleep(1)
        bag2.add('a')
        bag2['a'] = 1
        bag2.sync()
        self.assertTrue('a' in bag2)
        self.assertTrue(bag2['a'].value == 1)

        delete_bag(bag1)

    def test_AutoSyncFunction(self):
        
        bag1 = propbag(self._testMethodName, autosync = True)
        bag2 = propbag(self._testMethodName, autosync = True)

        # test adding items that were not present in other instances
        bag1.add(('a', 1))
        time.sleep(1)
        bag2.save()
        self.assertTrue('a' in bag2)

        # test updating items that are not marked as changed
        bag1.set({'a': 2})
        time.sleep(1)
        bag2.save()
        self.assertTrue(bag2['a'].value == 2)

        # test dropping items that are not marked as changed
        bag1.drop('a')
        time.sleep(1)
        bag2.save()
        self.assertFalse('a' in bag2)
        
        # test dropping
        """
         when dropping...
	        if exists...
		        if timestamp <=, do not delete (aka add it back to the bag)
		        if newer, do nothing, leave it deleted
	        if does not exist...
		        do nothing, leave it deleted
        """
        bag1.add(('b', 1))
        time.sleep(1)
        bag2.save()
        time.sleep(1)
        bag2 - 'b'
        self.assertFalse('b' in bag2)
        time.sleep(1)
        bag1['b'] = 2
        time.sleep(1)
        bag2.save()
        self.assertTrue('b' in bag2)
        self.assertTrue(bag2['b'].value == 2)
        time.sleep(1)
        bag2 - 'b'
        time.sleep(1)
        self.assertFalse('b' in bag2)
        bag2 + ('c', 1)
        self.assertTrue('c' in bag2)
        bag2 - 'c'
        self.assertFalse('c' in bag2)
        self.assertFalse('c' in bag2)
        time.sleep(1)

        # test adding
        """
         when adding...
	        if already exists...
		        if timestamp <=, update this instance value
		        if newer, do nothing, value is the latest
	        if does not exist...
		        do nothing, value is the latest
        """
        bag1 + ('d', 1)
        bag2 + ('d', 2)
        bag1['d'] = 3
        time.sleep(1)
        bag2.save()
        self.assertTrue(bag2['d'].value == 3)
        time.sleep(1)
        bag2['d'] = 4
        time.sleep(1)
        self.assertTrue(bag2['d'].value == 4)
        bag2 + ('e', 1)
        self.assertTrue(bag2['e'].value == 1)

        # test updating
        """
        when updating...
	        if exists...
		        if timestamp <=, update from file
		        if newer, do nothing, value is latest
	        if does not exist...
		        if timestamp <=, delete from this instance
                if newer, do nothing, value is latest
        """
        bag1.add('a')
        time.sleep(1)
        bag2['a'] = 9
        time.sleep(1)
        bag1['a'] = 10
        bag2.save()
        self.assertTrue(bag2['a'].value == 10)
        bag1['a'] = 11
        time.sleep(1)
        bag2['a'] = 20
        self.assertTrue(bag2['a'].value == 20)
        bag1 - 'a'
        time.sleep(1)
        bag2.save()
        self.assertFalse('a' in bag2)
        time.sleep(1)
        bag2.add('a')
        bag2['a'] = 1
        self.assertTrue('a' in bag2)
        self.assertTrue(bag2['a'].value == 1)

        delete_bag(bag1)
if __name__ == '__main__':
    unittest.main()
