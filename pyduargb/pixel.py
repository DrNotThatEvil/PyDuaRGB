from __future__ import print_function, absolute_import


class Pixel(object):
    """DuaRGB Pixel class for make handling of pixels easier"""

    def __init__(self, rgb, brightness = 1.0):
        """Pixel constructor"""
        super().__init__()
        self.rgb = rgb
        self.brightness = brightness
        self.translated = False

    def rgbmap_translate(self, rgbmap):
        if self.translated:
            return

        orignal_rgb = self.rgb
        rgbmap = rgbmap.lower()
        r_index = rgbmap.index('r')
        g_index = rgbmap.index('g')
        b_index = rgbmap.index('b')

        r = orignal_rgb['r']
        g = orignal_rgb['g']
        b = orignal_rgb['b']

        if r_index == 1:
            r = orignal_rgb['g']
        elif r_index == 2:
            r = orignal_rgb['b']

        if g_index == 0:
            g = orignal_rgb['r']
        elif g_index == 2:
            g = orignal_rgb['b']

        if b_index == 0:
            b = orignal_rgb['r']
        elif b_index == 1:
            b = orignal_rgb['g']

        self.rgb = {'r': r, 'g': g, 'b': b}
        self.translated = True

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
