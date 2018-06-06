from __future__ import print_function, absolute_import

import sys
import time
import math
from .base_chip import BaseChip

try:
    import spidev
except ImportError:
    from ..mock import spidev

CACHE_SIZE = 25000


class LPD6803(BaseChip):
    """
    Chip class for a LPD6803 based ledstrip.
    """

    CHIP_NAME = "LPD6803"
    PIXEL_SIZE = 3
    PIXEL_BYTES = 2

    def __init__(self):
        super().__init__()
        self.gamma = bytearray(256)
        self.gamma_select = 0
        self.spi = spidev.SpiDev()

        for i in range(256):
            self.gamma[i] = int(pow(float(i) / 255.0, 2.0) * 255.0 + 0.5)

    def calculate_gamma(self, pixel_in):
        if self.gamma_select == 1:
            pixel_in[0] = self.gamma[pixel_in[0]]
            pixel_in[1] = self.gamma[pixel_in[1]]
            pixel_in[2] = self.gamma[pixel_in[2]]
        return pixel_in

    def write_pixels(self, pixels, total_pixels, out):
        self.spi.open(0, 1)
        self.spi.max_speed_hz = 7800000
        hsh = hash(pixels)  # get hash of the pixels.

        # Write from cache if available
        if self._caching_enabled and self._is_in_cache(hsh):
            write = bytearray(4)
            write.extend(self._cache[hsh])
            self.spi.xfer(write)
            self.spi.close()
            return

        data = bytearray()

        pixel_count = len(pixels)
        for index in range(pixel_count):
            pixel_out_bytes = bytearray(2)
            pixel_in = self.calculate_gamma(pixels[index].get_bytearray(
                self.PIXEL_SIZE)
            )

            pixel_out = 0b1000000000000000  # bit 16 must be ON
            pixel_out |= (pixel_in[0] & 0x00F8) << 2
            pixel_out |= (pixel_in[1] & 0x00F8) << 7
            pixel_out |= (pixel_in[2] & 0x00F8) >> 3

            pixel_out_bytes[0] = (pixel_out & 0xFF00) >> 8
            pixel_out_bytes[1] = (pixel_out & 0x00FF) >> 0
            data.extend(pixel_out_bytes)

        write = bytearray(4)
        write.extend(data)
        self.spi.xfer(write)
        self.spi.close()
        self._put_in_cache(hsh, data)  # Write data to cache
        return


class LPD8806(BaseChip):
    """
    Chip class for a LPD8806
    """

    CHIP_NAME = "LPD8806"
    PIXEL_SIZE = 3

    def __init__(self):
        super().__init__()
        self.gamma = bytearray(256)
        self.gamma_select = 1

        for i in range(256):
            self.gamma[i] = 0x80 | int(
                pow(float(i) / 255.0, 2.5) * 127.0 + 0.5
            )

    def calucate_gamma(self, pixel_in):
        output_pixel = pixel_in
        if self.gamma_select == 1:
            output_pixel[0] = self.gamma[pixel_in[2]]
            output_pixel[1] = self.gamma[pixel_in[0]]
            output_pixel[2] = self.gamma[pixel_in[1]]

        if self.gamma_select == 2:
            output_pixel[0] = self.gamma[pixel_in[1]]
            output_pixel[1] = self.gamma[pixel_in[0]]
            output_pixel[2] = self.gamma[pixel_in[2]]

        return output_pixel

    def write_pixels(self, pixels, total_pixels, out):
        pixel_count = len(pixels)
        pixel_out = bytearray((self.PIXEL_SIZE * pixel_count))
        for index in range(pixel_count):
            out_index = (index * self.PIXEL_SIZE)
            pixel_in = self.calucate_gamma(pixels[index].get_bytearray(
                self.PIXEL_SIZE)
            )

            pixel_out[out_index:(out_index+self.PIXEL_SIZE)] = pixel_in

        out.write(pixel_out)
        out.write(bytearray([0 for x in range(self.PIXEL_SIZE+1)]))
        out.flush()
        return
