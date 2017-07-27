from __future__ import print_function, absolute_import
from time import sleep

from ..logging import *
from ..meta import Singleton
from ..chips import *

logger = get_logger(__file__)

class RGBController(Singleton):
    def __init__(self, chip, ledcount, spidev):
        self.chip = chip
        self.ledcount = ledcount
        self.spidevstr = spidev
        self.spidev = open(self.spidevstr, "wb")
        logger.info("RGBController intitalized.")
        logger.debug("RGBController chiptype: {}".format(chip.get_chipname()))
    
    def play_animation(self, duration, animation, step=0.001):
        #TODO implement slave led amount into playing the animation.
        for i in range(duration):
            pixels = animation.animate_ns(i, duration, self.ledcount)
            self.chip.write_pixels(pixels, self.ledcount, self.spidev)
            sleep(step/2)
