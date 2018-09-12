from __future__ import print_function, absolute_import
import datetime

from .animationqueue import *
from ..config import config_system
from ..rgbcontroller.rgbcontroller import *

class QueueItem(object):
    def __init__(self, duration, animation, runlevel, sticky=False, allow_lower_runlevel=False):
        self.duration = duration
        self.animation = animation
        self.runlevel = runlevel
        self.sticky = sticky
        self.allow_lower_runlevel = allow_lower_runlevel 
        self.ready = False
        self.pixels = []
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

    def get_ready(self):
        return self.ready

    def check_queue_permissions(self, queueitem):
        if(self.allow_lower_runlevel):
            return True

        if(self.runlevel <= queueitem.get_runlevel()):
            return True
        
        return False
    
    def calculate_task(self):
        """Calculate the pixels for this queueitem"""
        if self.ready:
            return

        pixels = []
        for i in range(self.duration):
            local_pixels = self.animation.animate_ns(i, self.duration, self._ledcount)
            if self._rgbmap != 'rgb':
                for pixel in local_pixels:
                    pixel.rgbmap_translate(self._rgbmap)
            pixels.append(local_pixels)
        self.pixels = pixels
        self.ready = True

    def perform_task(self):
        rgbcntl = RGBController()
        # rgb controller is a singleton
        # this is so i don't have to keep passing classes around
        rgbcntl.play_animation(self.duration, self.pixels)

    def to_json(self):
        return {
            "duration": self.duration,
            "animation": self.animation.to_json(),
            "runlevel": self.runlevel,
            "sticky": self.sticky,
            "allow_lower_runlevel": self.allow_lower_runlevel
        }

