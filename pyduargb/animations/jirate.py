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
from collections import deque
import math


from pyduargb.pixel import Pixel


class Jirate(object):
    def __init__(self, color, low=0.25, bright=1.0, timedelay=0.10):
        self.color = color
        self.low = low
        self.bright = bright
        self.timedelay = timedelay

    def animate_ns(self, i, duration, ledcount):
        percent = i / duration
        step = (1 / 0.10)

        brightness = 1.0
        ledbrightness = list()
        for x in range(ledcount):
            if ((x % 4) == 0):
                if(brightness == self.bright):
                    brightness = self.low
                elif(brightness == self.low):
                    brightness = self.bright

            ledbrightness.append(brightness)

        deque_brightness = deque(ledbrightness)
        shift = math.floor(i*self.timedelay) % ledcount
        deque_brightness.rotate(shift)

        return print([Pixel(self.color, x) for x in deque_brightness])

    def to_json(self):
        return {
            "name": "jirate",
            "color": self.color,
            "low": self.low,
            "bright": self.bright,
            "timedelay": self.timedelay
        }

    @staticmethod
    def can_be_cached():
        return True

    @staticmethod
    def from_json(obj):
        return Jirate(obj["color"], obj["low"], obj["bright"])
