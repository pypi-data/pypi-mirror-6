import unittest
import os
import os.path

from propdb.propbag import propbag, backendformat
from propdb.propbag import propitem

def delete_bag(bag):
    """ Deletes a propbag. """

    if isinstance(bag, propbag):
        if bag is not None and os.path.exists(bag.location):
            os.remove(bag.location)

class Test_TestBackend(unittest.TestCase):
    """ Tests the backend functionality """

    def test_JSONtoJSONFunction(self):
        """ Tests if a bag saved in JSON format can be opened as JSON. """

        bag = propbag(self._testMethodName, backend = backendformat.json)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        bag2 = propbag(self._testMethodName, backend = backendformat.json)

        for name in bag.names:
            self.assertTrue(name in bag2)

        delete_bag(bag)

    def test_PICKLEtoPICKLEFunction(self):
        """ Tests if a bag saved in PICKLE format can be opened as PICKLE. """

        bag = propbag(self._testMethodName, backend = backendformat.pickle)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        bag2 = propbag(self._testMethodName, backend = backendformat.pickle)

        for name in bag.names:
            self.assertTrue(name in bag2)

        delete_bag(bag)

    def test_JSONtoPICKLEFunction(self):
        """ Tests if a bag saved in JSON format can be opened as PICKLE. """

        bag = propbag(self._testMethodName, backend = backendformat.json)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        try:
            propbag(self._testMethodName, backend = backendformat.pickle)
        except ValueError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        delete_bag(bag)

    def test_PICKLEtoJSONFunction(self):
        """ Tests if a bag saved in PICKLE format can be opened as JSON. """

        bag = propbag(self._testMethodName, backend = backendformat.pickle)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        bag.add(bagItems)

        try:
            propbag(self._testMethodName, backend = backendformat.json)
        except ValueError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        delete_bag(bag)

if __name__ == '__main__':
    unittest.main()
