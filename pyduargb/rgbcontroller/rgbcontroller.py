from __future__ import print_function
import time
import datetime
import math

from ..logging import *
from ..meta import Singleton
from ..chips import *

logger = get_logger(__file__)


class RGBController(Singleton):
    def __init__(self, chip, ledcount, spidev, rgbmap):
        self.chip = chip
        self.ledcount = ledcount
        self.spidevstr = spidev
        self.rgbmap = rgbmap
        self.spidev = None
        # self.spidev = open(self.spidevstr, "wb")
        logger.info("RGBController intitalized.")
        logger.debug("RGBController chiptype: {}".format(chip.get_chipname()))

    def play_animation(self, duration, animation, step=1):
        # TODO implement slave led amount into playing the animation.
        start_mili = int(round(time.time() * 1000))
        for i in range(duration):
            pixels = animation.animate_ns(i, duration, self.ledcount)
            if self.rgbmap != 'rgb':
                for pixel in pixels:
                    pixel.rgbmap_translate(self.rgbmap)
            self.chip.set_caching(animation.can_be_cached())
            self.chip.write_pixels(pixels, self.ledcount, self.spidev)

        total_end = int(round(time.time() * 1000))
        logger.debug("total animation time: " + str(total_end - start_mili))
