from __future__ import print_function, absolute_import

import difflib
from pyduargb.pixel import Pixel

class BinaryCount(object):

    def __init__(self, ledcount):
        self._max_value = 2 ** ledcount
        self._value = 0

    def animate_ns(self, i, duration, ledcount):
        string = "{0:b}".format(self._value)
        string = string.zfill(ledcount)

        prev_string = "{0:b}".format(self._value-100)
        prev_string = prev_string.zfill(ledcount)

        self._value = self._value + 1
        return tuple([Pixel({'r': 0,
            'g': (0 if prev_string[count] == '0'
                and string[count] == '1' else 255),
            'b': (255 if prev_string[count] == '0'
                and string[count] == '1' else 0)}, 
            float(string[count])) for count in range(ledcount)])

    def to_json(self):
        return {"name": "binarycount"}

    @staticmethod
    def can_be_cached():
        return False

    @staticmethod
    def from_json(obj):
        return BinaryCount(obj["ledcount"])
