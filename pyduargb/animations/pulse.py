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
import math

from pyduargb.pixel import Pixel


class Pulse(object):

    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        increase = math.pi / duration
        brightness = math.sin(i * increase)

        return tuple([Pixel(self.color, brightness)
                     for count in range(ledcount)])

    def to_json(self):
        return {"name": "pulse", "color": self.color}

    @staticmethod
    def can_be_cached():
        return True

    @staticmethod
    def from_json(obj):
        return Pulse(obj["color"])
