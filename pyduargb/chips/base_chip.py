from __future__ import print_function, absolute_import

CACHE_SIZE = 15000 #15 Kb cache size.

class BaseChip(object):
    """The base chip for the a DuaRGB daemon

    This base chip should be extended by specific chips
    but must contain the following methods:

    TODO: WRITE ALL NESSECARY METHODS
    """

    CHIP_NAME = "base_chip"
    PIXEL_SIZE = 3
    PIXEL_BYTES = 2

    def __init__(self):
        super().__init__()
        self.gamma_select = 0  # Using this instead of a boolean multiple ways of gamma correction can be used.

    @classmethod
    def get_chipname(cls):
        return cls.CHIP_NAME

    def calculate_gamma(pixel_in):
        raise NotImplementedError('Error: calcuate_gamma is not implemented!')

    def write_pixels(pixels, total_pixels, out):
        """Write pixels to the ledstrip.

        Arguments:
        pixels -- List of Pixels
        total_pixels -- The amount of pixels on the strip.
        out -- The output for the bytes
        """
        raise NotImplementedError('Error: Extension of baseclass is needed')

