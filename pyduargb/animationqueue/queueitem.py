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

from .animationqueue import *
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

    def check_queue_permissions(self, queueitem):
        if(self.allow_lower_runlevel):
            return True

        if(self.runlevel <= queueitem.get_runlevel()):
            return True

        return False

    def perform_task(self):
        rgbcntl = RGBController()
        # rgb controller is a singleton
        # this is so i don't have to keep passing classes around
        rgbcntl.play_animation(self.duration, self.animation)

    def to_json(self):
        return {
            "duration": self.duration,
            "animation": self.animation.to_json(),
            "runlevel": self.runlevel,
            "sticky": self.sticky,
            "allow_lower_runlevel": self.allow_lower_runlevel
        }
