from __future__ import print_function, absolute_import

from random import randint
from pyduargb.pixel import Pixel

class RandomPixels(object):

    def __init__(self):
        self._pixels = None

    def animate_ns(self, i, duration, ledcount):
        if self._pixels is None or i == 0:
            self._pixels = [Pixel({'r':randint(0,255), 'g':randint(0,255), 'b': randint(0,255)}, 1.0) for count in range(ledcount)]
        return tuple(self._pixels)

    def to_json(self):
        return {"name": "randompixels"}

    @staticmethod
    def can_be_cached():
        return False

    @staticmethod
    def from_json(obj):
        return RandomPixels()
