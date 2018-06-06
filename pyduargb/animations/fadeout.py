from __future__ import print_function, absolute_import

from pyduargb.pixel import Pixel


class Fadeout(object):
    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        brightness = 1 - (i / duration)

        return tuple([Pixel(self.color, brightness)
                     for count in range(ledcount)])

    def to_json(self):
        return {"name": "fadeout", "color": self.color}

    @staticmethod
    def can_be_cached():
        return True

    @staticmethod
    def from_json(obj):
        return Fadeout(obj["color"])
