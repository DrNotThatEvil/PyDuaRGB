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
