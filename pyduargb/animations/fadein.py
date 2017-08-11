from __future__ import print_function, absolute_import

from pyduargb.pixel import Pixel

class Fadein(object):

    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        # animation pulses a single color 
        # animation takes 0.40 of the duration to fade in and out. The time in the middle 
        # the ledstrip will take to display the color statically

        brightness = i / duration

        return [Pixel(self.color, brightness) for count in range(ledcount)]

    def to_json(self):
        return {"name": "fadein", "color": self.color}

    @staticmethod
    def from_json(obj):
        return Fadein(obj["color"])
