from __future__ import print_function, absolute_import


class Pixel(object): 
    """DuaRGB Pixel class for make handling of pixels easier"""

    def __init__(self, rgb, brightness = 1.0):
        """Pixel constructor"""
        super().__init__()
        self.rgb = rgb
        self.brightness = brightness

    def get_brightness(self):
        return self.brightness

    def get_rgb(self):
        return self.rgb

    def get_raw_bytearray(self, pixel_size):
        out_bytes = bytearray(pixel_size)
        out_bytes[0] = self.rgb['r']
        out_bytes[1] = self.rgb['g']
        out_bytes[2] = self.rgb['b']
        return out_bytes

    def get_bytearray(self, pixel_size):
        raw_pixel = self.get_raw_bytearray(pixel_size)
        raw_pixel[0] = int(self.brightness * raw_pixel[0])
        raw_pixel[1] = int(self.brightness * raw_pixel[1])
        raw_pixel[2] = int(self.brightness * raw_pixel[2])
        return raw_pixel


