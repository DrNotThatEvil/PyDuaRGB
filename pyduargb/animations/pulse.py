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
