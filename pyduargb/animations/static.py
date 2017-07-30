from __future__ import print_function, absolute_import

from pyduargb.pixel import Pixel

class Static(object):

    def __init__(self, color, brightness):
        self.color = color
        self.brightness = brightness

    def animate_ns(self, i, duration, ledcount):
        return [Pixel(self.color, self.brightness) for count in range(ledcount)]

    def to_json(self):
        return {"name": "static", "color": self.color, "brightness": self.brightness}

    @staticmethod
    def from_json(obj):
        return Static(obj["color"], obj["brightness"])
