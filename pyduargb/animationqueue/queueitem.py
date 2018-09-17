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


from __future__ import print_function, absolute_import
import datetime
import time

from .animationqueue import *
from ..config import config_system
from ..rgbcontroller.rgbcontroller import *


class QueueItem(object):
    def __init__(self,
                 duration, animation, runlevel,
                 sticky=False, allow_lower_runlevel=False):
        self.duration = duration
        self.animation = animation
        self.runlevel = runlevel
        self.sticky = sticky
        self.allow_lower_runlevel = allow_lower_runlevel 
        self.ready = False
        self.being_computed = False
        self.pixels = []
        self.translated_pixels = []
        configsys = config_system.ConfigSystem()
        self._ledcount = configsys.get_option('main', 'leds').get_value()
        self._rgbmap = configsys.get_option('main', 'rgbmap').get_value()

    def get_duration(self):
        return self.duration

    def get_animation(self):
        return self.animation

    def get_runlevel(self):
        return self.runlevel

    def get_sticky(self):
        return self.sticky

    def get_allow_lower_runlevel(self):
        return self.allow_lower_runlevel

    def get_being_computed(self):
        return self.being_computed

    def get_ready(self):
        return self.ready

    def get_frames(self):
        # TODO rename the variable to frames since it's better
        return self.pixels

    def get_translated_frames(self):
        return self.translated_pixels

    def check_queue_permissions(self, queueitem):
        if(self.allow_lower_runlevel):
            return True

        if(self.runlevel <= queueitem.get_runlevel()):
            return True

        return False
    
    def calculate_task(self):
        """Calculate the pixels for this queueitem"""
        if self.ready or self.being_computed:
            return

        
        added_leds = masterdb.get_added_leds()

        self.being_computed = True
        pixels = []
        translated_pixels = []
        for i in range(self.duration):
            local_pixels = list(self.animation.animate_ns(i, self.duration, self._ledcount + added_leds))
            local_trans = local_pixels.copy()
            pixels.append(local_pixels)

            if not self._rgbmap == "rgb":
                for pixel in local_trans:
                    pixel.rgbmap_translate(self._rgbmap)
                translated_pixels.append(local_trans)
            else:
                translated_pixels.append(local_pixels)

        self.translated_pixels = translated_pixels
        self.pixels = pixels

        remote_pixels = []
        for x in self.pixels:
            remote_pixels.append(x[self._ledcount:]) 

        self.pixels = [x[0:self._ledcount] for x in self.pixels]
        self.translated_pixels = [x[0:self._ledcount] for x in self.translated_pixels]

        offset = 0
        for x in range(masterdb.get_last_index()):
            slave_leds = masterdb.get_slave_leds(x)
            masterdb.write_remote_frames(x, hash(self), remote_pixels[offset:slave_leds])
            offset = offset + slave_leds
       
        while (masterdb.get_total_unsend_length(hash(self)) > 0):
            if masterdb.get_total_unsend_length(hash(self)) == 0:
                break

        self.ready = True

    def perform_task(self):
        if not self.ready:
            return False

        # TODO move this use Scheduler.
        # TODO Is this method needed? 

        rgbcntl = RGBController()
        rgbcntl.play_animation(self.duration, self.pixels)
        return True

    def to_json(self):
        return {
            "duration": self.duration,
            "animation": self.animation.to_json(),
            "runlevel": self.runlevel,
            "sticky": self.sticky,
            "allow_lower_runlevel": self.allow_lower_runlevel
        }
