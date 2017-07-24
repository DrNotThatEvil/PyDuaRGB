from __future__ import print_function, absolute_import

import math
from .base_chip import BaseChip

class SM16716(BaseChip):
    """
    Chip class for a SM16716 based ledstrip.
    """

    CHIP_NAME = "SM16716"
    PIXEL_SIZE = 4

    def __init__(self):
        super().__init__()

    def write_pixels(self, pixels, total_pixels, out):
        out.write(bytearray(4))

        pixel_count = len(pixels)
        pixel_out = bytearray((self.PIXEL_SIZE * pixel_count))
        for index in range(pixel_count):
            out_index = (index * self.PIXEL_SIZE)
            pixel_in = pixels[index].get_bytearray(self.PIXEL_SIZE)

            pixel_in[1] = pixel_in[0]
            pixel_in[2] = pixel_in[1]
            pixel_in[3] = pixel_in[2]
            pixel_in[0] = 1  # The first led bit is always a 1

            pixel_out[out_index:(out_index+self.PIXEL_SIZE)] = pixel_in

        out.write(bytearray([0 for x in range(50)]) + pixel_out)
        return
