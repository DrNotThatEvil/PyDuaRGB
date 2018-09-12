# PyduaRGB: The python daemon for your ledstrip needs.
# Copyright (C) 2018 wilvin@wilv.in

# This program is free software: you can redistribute it and/or modify
# it under the terms of GNU Lesser General Public License version 3
# as published by the Free Software Foundation, Only version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function, absolute_import

from random import randint
from pyduargb.pixel import Pixel


class RandomPixels(object):
    def __init__(self):
        self._pixels = None

    def animate_ns(self, i, duration, ledcount):
        if self._pixels is None or i == 0:
            self._pixels = [Pixel({
                            'r': randint(0, 255),
                            'g': randint(0, 255),
                            'b': randint(0, 255)}, 1.0)
                            for count in range(ledcount)]
        return tuple(self._pixels)

    def to_json(self):
        return {"name": "randompixels"}

    @staticmethod
    def can_be_cached():
        return False

    @staticmethod
    def from_json(obj):
        return RandomPixels()
