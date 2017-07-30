from __future__ import print_function, absolute_import
from collections import deque
import math


from pyduargb.pixel import Pixel

class Jirate(object):

    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        # animation pulses a single color 
        # animation takes 0.40 of the duration to fade in and out. The time in the middle 
        # the ledstrip will take to display the color statically

        brightness = 1.0
        ledbrightness = list()
        for x in range(ledcount):
            if ((x % 4) == 0):
                if(brightness == 1):
                    brightness = 0.5
                elif(brightness == 0.5):
                    brightness = 1

            ledbrightness.append(brightness)
        
        deque_brightness = deque(ledbrightness)
        shift = i % ledcount
        deque_brightness.rotate(shift)
      
        print("{}: {}".format(i, deque_brightness))

        return [Pixel(self.color, x) for x in deque_brightness]

    def to_json(self):
        return {"name": "jirate", "color": self.color}

    @staticmethod
    def from_json(obj):
        return Jirate(obj["color"])
