from __future__ import print_function, absolute_import
from math import sin
from pyduargb.pixel import Pixel

class Racer(object):

    def __init__(self, color):
        self.color = color

    def animate_ns(self, i, duration, ledcount):
        percent = i / duration
        leader = sin( percent ) * ledcount
       
        arr = []
        for count in range(ledcount):
            brightness = 0
            if count >= (leader - 5) and count <= leader:
                brightness = 1.0
            arr.append(Pixel(self.color, brightness))
            
        return arr

    def to_json(self):
        return {"name": "racer", "color": self.color}

    @staticmethod
    def from_json(obj):
        return Pulse(obj["color"])
