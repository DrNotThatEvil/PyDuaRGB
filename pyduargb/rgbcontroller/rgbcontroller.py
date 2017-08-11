from __future__ import print_function, absolute_import
import time
import datetime
import math

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
    
    def play_animation(self, duration, animation, step=1):
        #TODO implement slave led amount into playing the animation.
        for i in range(duration):
            start = datetime.datetime.now()
            pixels = animation.animate_ns(i, duration, self.ledcount)
            self.chip.write_pixels(pixels, self.ledcount, self.spidev)
            end = datetime.datetime.now()
            delta = end - start
            step_micro = step * 1000
            if(delta.microseconds < step_micro):
                delay = (((step_micro - delta.microseconds)-100) / 1000000)
                time.sleep(delay)
