#!/usr/bin/env python
"""
Dispatching Dictionary
Matt Soucy

This class provides a way to forward lookups in a dictionary to a second dictionary
transparently, such that users cannot tell which dictionary the item is in.

This is useful in situations where a form of "dictionary inheritance" is needed,
to provide a convenient interface for situations where a core dictionary needs
to be updated, but other "derived" dictionaries need to look up items from it.
"""
from itertools import chain
from UserDict import DictMixin

class DispatchDict(DictMixin):
    '''
    Behaves as a dictionary, but provides an option to lookup keys in another dictionary
    '''

    def __init__(self, *args, **kwargs):
        '''
        Construct the internal dictionary like a builtin dictionary
        Specify the `dispatch` keyword argument to provide an alias
        '''
        self._alias = kwargs.pop("dispatch", None)
        self._dict = dict(*args, **kwargs)

    def dispatch(self, alias=None):
        '''
        Choose a new item to lookup items in
        '''
        self._alias = alias

    def get_dispatch(self):
        '''
        Get the item being dispatched to
        '''
        return self._alias

    def __getitem__(self, key):
        '''
        Get the item with the given key
        Uses the builtin dictionary, or the aliased one if possible
        '''
        if key in self._dict: return self._dict[key]
        elif self._alias: return self._alias[key]
        else: raise KeyError(key)

    def __setitem__(self, key, value):
        '''
        Set an item to a particular value
        Always assigns to the builtin, never the alias
        '''
        self._dict[key] = value
        return value

    def __delitem__(self, key):
        '''
        Remove an item from the dictionary
        May remove from the aliased dictionary
        '''
        if key in self._dict:
            del self._dict[key]
        elif self._alias:
            del self._alias[key]
        else:
            raise KeyError(key)

    def keys(self):
        '''
        List the keys in both dictionaries
        '''
        return set(self._dict.keys()) | set(self._alias.keys() if self._alias else [])

    def __iter__(self):
        '''
        Iterates over the builtin dictionary, then the alias
        '''
        if self._alias:
            return chain(self._dict, self._alias)
        else:
            return iter(self._dict)

    def __contains__(self, key):
        '''
        Test to see if the key exists in either of the dictionaries
        '''
        return key in self._dict or (self._alias and key in self._alias)
