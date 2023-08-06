import unittest
import os
import os.path
import m2secret

from propdb.propbag import *

def delete_bag(bag):
    """ Deletes a propbag. """

    if isinstance(bag, propbag):
        if bag is not None and os.path.exists(bag.location):
            os.remove(bag.location)

class Test_TestSecretKeyFunction(unittest.TestCase):
    """ Testing the encryption functionality. """

    def test_SecretKeyEncAndDecFunction(self):
        """ Tests if the secret_key encrypts and decrypts a bag. """

        encbag = propbag(self._testMethodName, secret_key = self._testMethodName)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        encbag.add(bagItems)

        decbag = propbag(self._testMethodName, secret_key = self._testMethodName)

        for name in encbag.names:
            self.assertTrue(name in decbag)

        delete_bag(encbag)

    def test_SecretKeyNoEncAndDecFunction(self):
        """ Tests if fails when decrypting a none encrypted bag. """

        encbag = propbag(self._testMethodName)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        encbag.add(bagItems)

        try:
            propbag(self._testMethodName, secret_key = self._testMethodName)
        except DecryptionError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        delete_bag(encbag)

    def test_SecretKeyEncAndNoDecFunction(self):
        """ Tests if fails when opening an encrypted bag without a secret key. """

        encbag = propbag(self._testMethodName, secret_key = self._testMethodName)
        
        bagItems = ('item1', 1, 'item2', 2, 'item3', 3, 'item4', 4 \
            , 'item5', 5, 'item6', 6, 'item7', 7, 'item8', 8)

        encbag.add(bagItems)

        try:
            propbag(self._testMethodName)
        except ValueError:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        delete_bag(encbag)

if __name__ == '__main__':
    unittest.main()
