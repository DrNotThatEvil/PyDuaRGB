from __future__ import print_function, absolute_import


class Pixel(object):
    """DuaRGB Pixel class for make handling of pixels easier"""

    def __init__(self, rgb, brightness = 1.0):
        """Pixel constructor"""
        super().__init__()
        self.r = rgb['r']
        self.b = rgb['b']
        self.g = rgb['g']
        self.brightness = brightness
        self.translated = False

    def rgbmap_translate(self, rgbmap):
        if self.translated:
            return

        original_r = self.r
        original_g = self.g
        original_b = self.b

        rgbmap = rgbmap.lower()
        r_index = rgbmap.index('r')
        g_index = rgbmap.index('g')
        b_index = rgbmap.index('b')

        r = original_r
        g = original_g 
        b = original_b

        if r_index == 1:
            r = original_g
        elif r_index == 2:
            r = original_b

        if g_index == 0:
            g = original_r 
        elif g_index == 2:
            g = original_b

        if b_index == 0:
            b = original_r
        elif b_index == 1:
            b = original_g

        self.r = r
        self.g = g
        self.b = b
        self.translated = True

    def __eq__(self, other):
        return (self.r == other.r and self.g == other.g and self.b == other.b 
                and self.brightness == other.brightness)

    def __hash__(self):
        return hash((self.r, self.g, self.b, self.brightness))

    def get_brightness(self):
        return self.brightness

    def get_rgb(self):
        return {'r': self.r, 'g': self.g, 'b': self.b}

    def get_raw_bytearray(self, pixel_size):
        out_bytes = bytearray(pixel_size)
        out_bytes[0] = self.r
        out_bytes[1] = self.g
        out_bytes[2] = self.b
        return out_bytes

    def get_bytearray(self, pixel_size):
        raw_pixel = self.get_raw_bytearray(pixel_size)
        raw_pixel[0] = int(self.brightness * raw_pixel[0])
        raw_pixel[1] = int(self.brightness * raw_pixel[1])
        raw_pixel[2] = int(self.brightness * raw_pixel[2])
        return raw_pixel
