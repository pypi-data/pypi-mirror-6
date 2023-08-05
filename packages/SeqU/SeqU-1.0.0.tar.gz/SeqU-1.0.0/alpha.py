#!/usr/bin/env python
# Copyright © 2013 Cameron Brandon White

class Alpha:
    """ A single character from 'a' to 'z' """

    def __init__(self, value):
        """ Alpha can be initilized with a number of a letter.
        The letter must be in the alphabet. You may give either
        an upper case or lower case letter. Alpha interprets 0
        as 'a' and 25 as 'z'. Any number greater than 25 is
        rolled back to 0 with mod.
        """

        try:
            value = chr(int(value)%26+ord('a')-1)
        except ValueError:
            if type(value) is str:
                if len(value) is not 1:
                    raise ValueError("one character only")

        if value.isalpha():
            self._value = value
        else:
            raise ValueError("must a letter in the alphabet")

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return "Alpha('{}')".format(self._value)

    def __float__(self):
        return float(int(self))

    def __format__(self, format_spec):
    
        type_char = format_spec[-1]
        if type_char not in ['a', 'A']:
            raise ValueError(
                "Unknown format code '{}' for object in type {}".format(
                    type_char, type(self)))
    
        func = str.upper if str.isupper(type_char) else str.lower
        return format(func(str(self)), format_spec[:-1])

    def __int__(self):
        base = ord('a') if self._value.islower() else ord('A') 
        return ord(self._value) - base + 1
    
    def __add__(self, other):

        return Alpha(int(self)+int(other))
