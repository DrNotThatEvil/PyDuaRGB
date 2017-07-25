from __future__ import print_function, absolute_import

import math
from .base_chip import BaseChip


class LPD6803(BaseChip):
    """
    Chip class for a LPD6803 based ledstrip.
    """

    CHIP_NAME = "LPD6803"
    PIXEL_SIZE = 3

    def __init__(self):
        super().__init__()
        self.gamma = bytearray(256)
        self.gamma_select = 1

        for i in range(256):
            self.gamma[i] = int(pow(float(i) / 255.0, 2.0) * 255.0 + 0.5)

    def calculate_gamma(self, pixel_in):
        if self.gamma_select == 1:
            pixel_in[0] = self.gamma[pixel_in[0]]
            pixel_in[1] = self.gamma[pixel_in[1]]
            pixel_in[2] = self.gamma[pixel_in[2]]
        return pixel_in

    def write_pixels(self, pixels, total_pixels, out):
        pixel_out_bytes = bytearray(2)
        out.write(bytearray(4))

        pixel_count = len(pixels)
        for index in range(pixel_count):
            pixel_in = self.calculate_gamma(pixels[index].get_bytearray(self.PIXEL_SIZE))

            pixel_out = 0b1000000000000000  # bit 16 must be ON
            pixel_out |= (pixel_in[0] & 0x00F8) << 7  # RED is bits 11-15
            pixel_out |= (pixel_in[1] & 0x00F8) << 2  # GREEN is bits 6-10
            pixel_out |= (pixel_in[2] & 0x00F8) >> 3  # BLUE is bits 1-5

            pixel_out_bytes[0] = (pixel_out & 0xFF00) >> 8
            pixel_out_bytes[1] = (pixel_out & 0x00FF) >> 0
            out.write(pixel_out_bytes)
        out.write(bytearray(int(math.ceil(len(pixels) / 8 + 1))))
        out.flush()
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
            self.gamma[i] = 0x80 | int(pow(float(i) / 255.0, 2.5) * 127.0 + 0.5)
    
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
            pixel_in = self.calucate_gamma(pixels[index].get_bytearray(self.PIXEL_SIZE))
            
            pixel_out[out_index:(out_index+self.PIXEL_SIZE)] = pixel_in
        
        out.write(pixel_out)
        out.write(bytearray([0 for x in range(self.PIXEL_SIZE+1)]))
        out.flush()
        return
