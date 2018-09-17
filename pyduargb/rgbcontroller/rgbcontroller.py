# PyduaRGB: The python daemon for your ledstrip needs.
# Copyright (C) 2018 wilvin@wilv.in

# This program is free software: you can redistribute it and/or modify
# it under the terms of GNU Lesser General Public License version 3
# as published by the Free Software Foundation, Only version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function
import time
import datetime
import math
import threading

from ..logging import *
from ..meta import Singleton
from ..pixel import Pixel
from ..chips import *
from ..masterslave.master.masterdata import MasterData

masterdb = MasterData()
logger = get_logger(__file__)


class RGBController(Singleton):
    def __init__(self, chip, ledcount, spidev, rgbmap, is_slave):
        self.chip = chip
        self.ledcount = ledcount
        self.spidevstr = spidev
        self.rgbmap = rgbmap
        self.spidev = None
        self._stop_event = threading.Event()
        # self.spidev = open(self.spidevstr, "wb")
        logger.info("RGBController intitalized.")
        logger.debug("RGBController chiptype: {}".format(chip.get_chipname()))
   
    def display_frame(self, frame):
        if isinstance(frame, list): 
            frame = tuple([Pixel({'r': x[0], 'g':x[1], 'b':x[2]}) for x in frame])
            print("Test")
        
        self.chip.write_pixels(frame, self.ledcount, self.spidev)

    def play_animation(self, duration, all_pixels):
        for pixels in all_pixels:
            self.chip.write_pixels(pixels, self.ledcount, self.spidev)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def process_master_leds(self, pixel_bytes):
        # Convert the leds to pixel objects.
        pixels = [Pixel({'r': x[0], 'g':x[1], 'b':x[2]}) for x in pixel_bytes]
        if self.rgbmap != 'rgb':
            for pixel in pixels:
                pixel.rgbmap_translate(self.rgbmap)
        self.chip.set_caching(False)
        self.chip.write_pixels(tuple(pixels), self.ledcount, self.spidev)

    def old_play_animation(self, duration, animation, step=1):
        # TODO implement slave led amount into playing the animation.
        start_mili = int(round(time.time() * 1000))
        for i in range(duration):
            if self.stopped():
                logger.info("RGBController force stopping animation.")
                break

            # Get the added leds from the slaves (that are in continue mode)
            total_leds = self.ledcount + masterdb.get_added_leds()
            all_pixels = list(animation.animate_ns(i, duration, total_leds))
            pixels = tuple(all_pixels[0:self.ledcount])  # cut remote leds.

            masterdb.write_remote_leds(all_pixels[self.ledcount:])

            if self.rgbmap != 'rgb':
                for pixel in pixels:
                    pixel.rgbmap_translate(self.rgbmap)
            self.chip.set_caching(animation.can_be_cached())
            self.chip.write_pixels(pixels, self.ledcount, self.spidev)

        total_end = int(round(time.time() * 1000))
        logger.debug("total animation time: " + str(total_end - start_mili))
