#!/usr/bin/env python

import io
import json
import os
import os.path
import cPickle
import tempfile
import time

from propitem import propitem, actiontype

encryption_exists = True

try:
    import hmac
    import cStringIO
    from hashlib import sha256
    from binascii import hexlify, unhexlify
    from M2Crypto import EVP
except ImportError:
    encryption_exists = False

class backendformat:
    json, pickle = range(2)

    @staticmethod
    def is_supported(value):
        """ Returns true of the format is supported. """

        if value == backendformat.json or value == backendformat.pickle:
            return True
        else:
            return result

class propbag(object):
    """ This class defines a property bag for storing property items. """

    def __init__(self, name = None, directory = None, autosave = True, secret_key = None
                 , backend = backendformat.json, autosync = False):
        """ The bag initializer prefers a name but is not required. If name is None then a name will be
        created for the bag. 
        
        name = Name of the bag. The name becomes the name of the file as well.
        directory = The folder location of the bag.
        autosave = If True, then the bag will save itself as changes are set.
        secret_key = If set with a string (max length 32), then the bag will be encrypted.
        backend = This defines how the bag is serialized to the file system.
        autosync = Set to True if two separate instances are accessing the same
            bag. The bags will remain in sync.

        """

        self.__is_dirty = False
        self.__suspend_autosave = False
        self.__items = {}

        self.__backend = backendformat.json

        if backendformat.is_supported(backend):
            self.__backend = backend

        self.__folder = os.getcwd()

        if directory is not None and len(directory) > 0 and os.path.exists(directory):
            self.__folder = directory

        if name is None or len(name) == 0:
            temp_file_handle, temp_file_name = tempfile.mkstemp(dir = self.__folder)
            self.__name = os.path.basename(temp_file_name)
            os.close(temp_file_handle)
            os.remove(temp_file_name)
        else:
            self.__name = name

        self.__secret_key = None
        self.__encryptor = None

        if secret_key is not None:
            if len(secret_key) == 0:
                raise ValueError("Secret key cannot be blank.")
            else:
                global encryption_exists

                if encryption_exists:

                    self.__secret_key = secret_key[0:32] if len(secret_key) > 32 else secret_key
                    self.__encryptor = secret_cryptor()

                else:
                    raise ImportError("The propdb package uses the encryption package named M2Crypto" \
                        " and it is not installed; therefore, the secret_key option cannot be used." \
                        " Go to 'https://pypi.python.org/pypi/M2Crypto' for information on how to" \
                        " install the encryption module.")

        self.__autosave = autosave
        self.__autosync = autosync
        self.__last_sync = None
        self.__suspend_autosync = False

        self.__dropped_items = {}

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
                self.__set(name, value.value)
            else:
                self.__set(name, value)

            if self.__autosave and not self.__suspend_autosave:
                self.save()

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
    def name(self):
        """ Returns the name of the bag. """

        return self.__name

    @property
    def directory(self):
        """ Returns the name of the directory. """

        return self.__folder

    @property
    def is_dirty(self):
        """ Returns True if one of the items in the property bag have
        changed since last saved. """

        return self.__is_dirty
    
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
            for name, value in items.iteritems():
                if isinstance(name, basestring):
                    if name not in items_dict:
                        items_dict[name] = value

        # items is a propitem
        elif isinstance(items, propitem):
            if items.name not in items_dict:
                items_dict[items.name] = items.value

        # add the parsed items that are now in items_dict
        for name, value in items_dict.iteritems():
            added = self.__add(propitem(name, value))
            if added:
                result.append(added)

        if self.__autosave and not self.__suspend_autosave:
            self.save()

        return result

    def __add(self, item):
        """ The internal add function. """

        result = None

        if item.name not in self.__items:
            item.action_type = actiontype.add
            item.is_dirty = True
            self.__items[item.name] = item
            self.__is_dirty = True
            result = item.clone()

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
            result += self.__drop(items)
        elif isinstance(items, (list, tuple)):
            # iterate collection and drop by name or propitem
            for i in items:
                if isinstance(i, basestring):
                    result += self.__drop(i)
                elif isinstance(i, propitem):
                    result += self.__drop(i.name)
        elif isinstance(items, propitem):
            # drop by propitem
            result += self.__drop(items.name)

        if self.__autosave and not self.__suspend_autosave:
            self.save()

        return result

    def __drop(self, name):
        """ The internal drop function. """

        result = 0

        if name in self.__items:
            self.__dropped_items[name] = time.time()
            del self.__items[name]
            self.__is_dirty = True
            result = 1

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
            updated = self.__set(name, value)
            if updated:
                result.append(updated)

        if self.__autosave and not self.__suspend_autosave:
            self.save()

        return result

    def __set(self, n, v):
        """ The internal set function. """

        result = None

        if n in self.__items:
            self.__items[n].value = v
            self.__items[n].action_type = actiontype.set
            self.__is_dirty = True
            result = self.__items[n].clone()

        return result

    def save(self):
        """ Saves the property bag. """

        if self.is_dirty:
            # if it's dirty then it will save and sync if autosync is true
            if self.__save() != len(self.__items):
                raise IOError('Failed to save all the items.')
        else:
            # if not dirty but autosync is true then sync and see if dirty
            if self.__autosync and not self.__suspend_autosync:
                # suspend autosave so we do not get into loop of sync/save/sync/save etc
                suspend_autosave_setting = self.__suspend_autosave
                self.__suspend_autosave = True
                self.sync()
                self.__suspend_autosave = suspend_autosave_setting

                # if dirty after sync then save but suspend autosync so we
                # do not get into loop of save/sync/save/sync etc
                if self.is_dirty:
                    suspend_autosync_setting = self.__suspend_autosync
                    self.__suspend_autosync = True
                    if self.__save() != len(self.__items):
                        raise IOError('Failed to save all the items.')
                    self.__suspend_autosync = suspend_autosync_setting

    def suspend_autosave(self):
        """ Suspends the autosave feature. Use when changing multiple property items while
        autosave feature is activated. Forcing a save, even while suspended, is possible by
        calling the save method. """

        self.__suspend_autosave = True

    def resume_autosave(self):
        """ Resumes automatically saving when the autosave feature is activated.
        If the bag is dirty and the autosave feature is enabled then the bag
        will be saved. """

        self.__suspend_autosave = False

        if self.__autosave:
            self.save()

    def sync(self):
        """ Sync's the property bag that is in memory with the version that is saved on the file system.
        Use this feature when a property bag is being accessed by multiple instances. """

        f_bag_time = float(0)
        f_bag = None

        if os.path.exists(self.location):
            f_bag_time = os.path.getmtime(self.location)
            if f_bag_time > self.__last_sync:
                f_bag = propbag(name = self.name, directory = self.directory)

        if f_bag is not None:
            
            """
            hadle the dropped items first.

            when dropping...
	            if exists...
		            if timestamp <=, do not delete (aka add it back to the bag)
		            if newer, do nothing, leave it deleted
	            if does not exist...
		            do nothing, leave it deleted

            """
            dropped_items = []
            for name, timestamp in self.__dropped_items.iteritems():
                if name in f_bag:
                    if timestamp <= f_bag_time:
                        # adding it back because another instance has modified this item
                        # after this instance deleted therefore it must be needed.
                        self.__add(f_bag[name])
                    else:
                        dropped_items.append(name)

            self.__dropped_items = {}

            # now handle all the added and updated items.
            droplist = []
            for name, item in self.__items.iteritems():

                """
                when adding...
	            if already exists...
		            if timestamp <=, update this instance value
		            if newer, do nothing, value is the latest
	            if does not exist...
		            do nothing, value is the latest
                """
                if item.is_dirty and item.action_type == actiontype.add:
                    if item.name in f_bag:
                        if item.timestamp <= f_bag_time:
                            self.__set(item.name, f_bag[item.name].value)

                """
                when updating...
	            if exists...
		            if timestamp <=, update from file
		            if newer, do nothing, value is latest
	            if does not exist...
		            if timestamp <=, delete from this instance
                    if newer, do nothing, value is latest
                """
                if item.is_dirty and item.action_type == actiontype.set:
                    if item.name in f_bag:
                        if item.timestamp <= f_bag_time:
                            self.__set(item.name, f_bag[item.name].value)
                    else:
                        if item.timestamp <= f_bag_time:
                            droplist.append(item.name)

            # drop any items from the droplist
            for name in droplist:
                self.__drop(name)

            # update all items not marked as changed
            for name, value in self.__items.iteritems():
                if value.action_type == actiontype.none:
                    if name in f_bag:
                        if value.value != f_bag[name].value:
                            value.value = f_bag[name].value

            # now add all new items
            for item in f_bag.items:
                if item.name not in self.__items \
                    and item.name not in dropped_items:
                    self.__add(propitem(item.name, item.value))

            # drop items not marked as changed
            droplist = []
            for name, value in self.__items.iteritems():
                if value.action_type == actiontype.none \
                    and name not in f_bag:
                    droplist.append(name)

            # drop any items from the droplist
            for name in droplist:
                self.__drop(name)

        if self.__autosave and not self.__suspend_autosave:
            self.save()

    def suspend_autosync(self):
        """ Suspends the autosync feature. Use when changing multiple items while
        autosync feature is activated. Forcing a sync, even while suspended, is
        possible by calling the sync method directly. """

        self.__suspend_autosync = True

    def resume_autosync(self):
        """ Resumes automatically sync'ing when the autosync feature is activated.
        If the autosync feature is enabled then the bag will be sync'd. """

        self.__suspend_autosync = False

        if self.__autosync:
            self.sync()

    def __init(self):
        ''' Internal iniatizer that either creates or loads the property bag. '''

        if os.path.exists(os.path.join(self.__folder, self.__name)):
            with open(os.path.join(self.__folder, self.__name), 'r') as f:
                if self.__secret_key is not None:
                    decryptor = secret_cryptor()

                    try:
                        decryptor.deserialize(f.read())
                    except:
                        DecryptionError('Failed to deserialize propbag.')

                    try:
                        if self.__backend == backendformat.pickle:
                            contents = cPickle.loads(decryptor.decrypt(self.__secret_key))
                        else:
                            contents = json.loads(decryptor.decrypt(self.__secret_key))
                    except:
                        raise DecryptionError('Failed to decrypt propbag.')

                    decryptor.clear()
                else:
                    try:
                        if self.__backend == backendformat.pickle:
                            contents = cPickle.load(f)
                        else:
                            contents = json.load(f)
                    except:
                        raise ValueError("Failed to load propbag. The propbag data is " \
                            "corrupted or the backend format is different.")

                for name, value in contents.iteritems():
                    if isinstance(name, basestring) and name not in self.__items:
                        item = propitem(name, value)
                        item.action_type = actiontype.none
                        item.is_dirty = False
                        self.__items[name] = item
            
        else:
            # marking as dirty because it is new and if autosave is false then the
            # property bag will not be saved until save() is called
            self.__is_dirty = True
            if self.__autosave:
                self.save()

        self.__last_sync = time.time()

    def __save(self):
        ''' Saves the items dictionary to the file system as a serialized JSON object. '''

        if self.__autosync and not self.__suspend_autosync:
            suspend_autosave_setting = self.__suspend_autosave;
            self.__suspend_autosave = True
            self.sync()
            self.__suspend_autosave = suspend_autosave_setting

        # build a serializable dictionary from items
        contents = {}
        for name, value in self.__items.iteritems():
            contents[name] = value.value

        # encrypt data before opening the file
        if self.__secret_key is not None and self.__encryptor is not None:
            if self.__backend == backendformat.pickle:
                self.__encryptor.encrypt(cPickle.dumps(contents), self.__secret_key)
            else:
                # json is default
                self.__encryptor.encrypt(json.dumps(contents), self.__secret_key)

        with io.FileIO(os.path.join(self.__folder, self.__name), 'w') as f:
            if self.__secret_key is not None and self.__encryptor is not None:
                f.write(self.__encryptor.serialize())
            else:
                if self.__backend == backendformat.pickle:
                    cPickle.dump(contents, f)
                else:
                    # json is default
                    json.dump(contents, f)

        # mark bag as clean
        self.__is_dirty = False

        # update items as clean and action type as none
        for item in self.__items.itervalues():
            item.is_dirty = False
            item.action_type = actiontype.none

        # mark last sync
        self.__last_sync = time.time()

        # return number of items saved
        return len(contents)

class NoDataError(StandardError):
    """ This exception will be raised if we don't have data to encrypt/decrypt. """

    pass

class DecryptionError(StandardError):
    """ Failed to decrypt. """

    pass

class EncryptionError(StandardError):
    """ Failed to encrypt. """

    pass

class secret_cryptor(object):
    """ A secret is a wrapper class for the M2Crypto package. """

    def __init__(self, iv=None, salt=None, ciphertext=None,
                 iterations=1000, algorithm='aes_256_cbc'):
        """  Construct a Secret object.
        
        ciphertext, iv and salt can be None when originally created. The Secret
        is then considered to not hold any data. To set new data, call
        encrypt().
        
        @param iv: The IV, 256 bits (byte string 32 long)
        @param salt: The salt, 256 bits (byte string 32 long)
        @param ciphertext: The secret to hold
        @param iterations: The number of iterations to use with PBKDF2,
                           recommend 1000.
        @param param: The algorithm to use, recommend aes_256_cbc.

        """
        self.ciphertext = ciphertext
        self.iv = iv
        self.salt = salt
        self.iterations = iterations
        self.algorithm = algorithm

    def decrypt(self, password):
        """  Decrypt.

        @param password: The password to decrypt data with.
        @return: Decrypted data

        """
        if not self.ciphertext or not self.iv or not self.salt or \
            password is None:
            raise NoDataError
                
        # If the password is callable we'll assume it will return the
        # real password.
        try:
            password = password()
        except TypeError:
            pass
        
        # the crypto algorithms are unicode unfriendly
        if isinstance(password, unicode):
            password = password.encode('utf8')
        
        # derive 256 bit key using the pbkdf2 standard
        key = EVP.pbkdf2(password, self.salt, iter=self.iterations, keylen=32)

        # Derive encryption key and HMAC key from it
        # See Practical Cryptography section 8.4.1.
        hmacKey = sha256(key + 'MAC').digest()
        encKey = sha256(key + 'encrypt').digest()
        del key
        
        # decrypt
        try:
            ret = self.__decrypt(self.ciphertext, encKey, self.iv, self.algorithm)
        except EVP.EVPError, e:
            raise DecryptionError(str(e))
        finally:
            del encKey
        
        # Check MAC
        mac = ret[-64:]
        ret = ret[:-64]
        try:
            if hmac.new(hmacKey, ret + self.iv + self.salt,
                        sha256).hexdigest() != mac:
                raise DecryptionError('HMAC does not match')
        finally:
            del hmacKey

        return ret

    def encrypt(self, cleartext, password):
        """ Encrypt.
        
        @param cleartext: The data to encrypt.
        @param password: The password to encrypt data with.
        @return: Encrypted data

        """
        if cleartext is None or password is None:
            raise NoDataError
                
        # If the password is callable we'll assume it will return the
        # real password.
        try:
            password = password()
        except TypeError:
            pass
            
        # the crypto algorithms are unicode unfriendly
        if isinstance(password, unicode):
            password = password.encode('utf8')
        
        # get 256 bit random encryption salt
        self.salt = os.urandom(32)
        # derive 256 bit encryption key using the pbkdf2 standard
        key = EVP.pbkdf2(password, self.salt, iter=self.iterations, keylen=32)
        
        # Derive encryption key and HMAC key from it
        # See Practical Cryptography section 8.4.1.
        hmacKey = sha256(key + 'MAC').digest()
        encKey = sha256(key + 'encrypt').digest()
        del key

        # get 256 bit random iv
        self.iv = os.urandom(32)

        # Add HMAC to cleartext so that we can check during decrypt if we got
        # the right cleartext back. We are doing sign-then-encrypt, which let's
        # us encrypt empty cleartext (otherwise we'd need to pad with some
        # string to encrypt). Practical Cryptography by Schneier & Ferguson
        # also recommends doing it in this order in section 8.2.
        mac = hmac.new(hmacKey,
                       cleartext + self.iv + self.salt,
                       sha256).hexdigest()
        del hmacKey

        # encrypt
        try:
            self.ciphertext = self.__encrypt(cleartext + mac, encKey, self.iv,
                                      self.algorithm)
        except EVP.EVPError, e:
            raise EncryptionError(str(e))

        return self.ciphertext

    def serialize(self, serialize=None):
        """ Serialize secret.
        
        @param serialize: None or callable that must accept string to serialize
        @return: Serialized string

        """
        if not self.ciphertext or not self.iv or not self.salt:
            raise NoDataError

        serialized = "%s|%s|%s" % (hexlify(self.iv), hexlify(self.salt),
                                    hexlify(self.ciphertext))
        if serialize is not None:
            serialize(serialized)
        return serialized

    def deserialize(self, deserialize):
        """ Deserialize secret.
        
        @param deserialize: String or callable that must return the serialized form.

        """
        try:
            serialized = deserialize()
        except TypeError:
            serialized = deserialize 

        iv, salt, ciphertext = serialized.split('|')
        self.iv, self.salt, self.ciphertext = unhexlify(iv), unhexlify(salt), unhexlify(ciphertext) 

    def clear(self):
        """ Clears the internal secret data. """

        try:
            del self.ciphertext
        except AttributeError:
            pass
        try:
            del self.iv
        except AttributeError:
            pass
        try:
            del self.salt
        except AttributeError:
            pass

    def __cipherFilter(self, cipher, inf, outf):
        """ A helper function to decrypt/encrypt. """

        while 1:
            buf = inf.read()
            if not buf:
                break
            outf.write(cipher.update(buf))
        outf.write(cipher.final())
        return outf.getvalue()

    def __decrypt(self, ciphertext, key, iv, alg):
        """ Decrypt ciphertext """

        assert len(key) == len(iv) == 32
        cipher = EVP.Cipher(alg=alg, key=key, iv=iv, op=0)
        del key
        pbuf = cStringIO.StringIO()
        cbuf = cStringIO.StringIO(ciphertext)
        plaintext = self.__cipherFilter(cipher, cbuf, pbuf)
        pbuf.close()
        cbuf.close()
        return plaintext

    def __encrypt(self, plaintext, key, iv, alg):
        """ Encrypt plaintext """

        assert len(key) == len(iv) == 32
        cipher = EVP.Cipher(alg=alg, key=key, iv=iv, op=1)
        del key
        pbuf = cStringIO.StringIO(plaintext)
        cbuf = cStringIO.StringIO()
        ciphertext = self.__cipherFilter(cipher, pbuf, cbuf)
        pbuf.close()
        cbuf.close()
        assert ciphertext
        return ciphertext
        