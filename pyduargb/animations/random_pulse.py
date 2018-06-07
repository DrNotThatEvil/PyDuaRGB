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


class RandomPulse(object):
    def __init__(self):
        self.current_color = {
            'r': randint(0, 255),
            'g': randint(0, 255),
            'b': randint(0, 255)
        }

    def animate_ns(self, i, duration, ledcount):
        if i == 0:
            self.current_color = {
                'r': randint(0, 255),
                'g': randint(0, 255),
                'b': randint(0, 255)
            }

        percent = i / duration
        step = (1 / 0.40)
        brightness = 0

        brightness = 0.0 + (percent * step)

        if (percent > 0.40 and percent < 0.60):
            brightness = 1.0

        if (percent >= 0.60):
            brightness = 0.0 + ((percent-0.60) * step)
            brightness = 1.0 - brightness

        if (percent == 1.0):
            brightness = 0

        return tuple([Pixel(self.current_color, brightness)
                      for count in range(ledcount)])

    def to_json(self):
        return {"name": "random_pulse"}

    @staticmethod
    def can_be_cached():
        return False

    @staticmethod
    def from_json(obj):
        return RandomPulse()
