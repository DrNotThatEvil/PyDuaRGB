from __future__ import print_function, absolute_import

from pyduargb.pixel import Pixel

class Static(object):

    def __init__(self, color, brightness):
        self.color = color
        self.brightness = brightness
        self._pixel_cache = None

    def animate_ns(self, i, duration, ledcount):
        if self._pixel_cache is None:
            self._pixel_cache = [Pixel(self.color, self.brightness) for count in range(ledcount)]
        return self._pixel_cache

    def to_json(self):
        return {"name": "static", "color": self.color, "brightness": self.brightness}

    @staticmethod
    def can_be_cached():
        return True

    @staticmethod
    def from_json(obj):
        return Static(obj["color"], obj["brightness"])
