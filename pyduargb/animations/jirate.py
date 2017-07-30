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
        # animation pulses a single color 
        # animation takes 0.40 of the duration to fade in and out. The time in the middle 
        # the ledstrip will take to display the color statically

        
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
      
        return [Pixel(self.color, x) for x in deque_brightness]

    def to_json(self):
        return {"name": "jirate", "color": self.color}

    @staticmethod
    def from_json(obj):
        return Jirate(obj["color"], obj["low"], obj["bright"])
