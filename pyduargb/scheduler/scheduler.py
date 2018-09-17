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

from __future__ import print_function, absolute_import, unicode_literals

import time
import threading

from ..masterslave.master.masterdata import MasterData
from ..rgbcontroller import rgbcontroller
from ..logging import *

logger = get_logger(__file__)
masterdb = MasterData()


class SlaveSchedulerThread(threading.Thread):
    def __init__(self, scheduler): 
        super(SlaveSchedulerThread, self).__init__()
        self._scheduler = scheduler
        self._stop_event = threading.Event()
        self._animations = {}
   
    def add_animation(self, header, start_time, frames, repeat):
        if header not in list(self._animations):
            self._animations[header] = [start_time, frames, repeat]

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            if self.stopped():
                break

            if len(self._animations) > 0:
                first_animation = list(self._animations)[0]
                animation = self._animations[first_animation]

                logger.debug("Starting item at:{0}".format(animation[0]))
                now = self._scheduler.time()
                while now < animation[0]:
                    now = self._scheduler.time()
                
                logger.debug("Starting item...")
                rgbcontrol = rgbcontroller.RGBController()
                
                for frame in animation[1]:
                    rgbcontrol.display_frame(tuple(frame))
                    now = self._scheduler.time()
                    frame_time = now + 0.010
                    while now < frame_time:
                        now = self._scheduler.time()

                if not animation[2]:
                    self._animations.pop(first_animation)
                else:
                    if len(self._animations) > 1:
                        self._animations.pop(first_animation)

class Scheduler(object):
    START_DELAY = 5

    def __init__(self):
        self._offset = 0
        self._last_sticky = None
 
    def set_offset(self, offset):
        self._offset = offset

    def time(self):
        return time.time() + self._offset

    def start(self, task):
        # Select a start time.
        # Send start time to slaves
        # Start the animation.

        rgbcontrol = rgbcontroller.RGBController()
        frames = task.get_translated_frames()
        if task.get_sticky() and task == self._last_sticky:
            for frame in frames:
                rgbcontrol.display_frame(tuple(frame))
                now = time.time()
                frame_time = now + 0.010
                while now < frame_time:
                    now = time.time()

            return
        elif task.get_sticky() and not task == self._last_sticky:
            self._last_sticky = task
        
        now = time.time()
        start_time = now + Scheduler.START_DELAY
        
        # TODO write good start that uses correct index
        masterdb.write_start(0, hash(task), start_time, task.get_sticky())

        logger.debug("Starting item at:{0}".format(start_time))

        # TODO allow this to be stopped.. incase of cntl+c
        while now < start_time:
            now = time.time()
       
        logger.debug("Starting item...")

        # Start the animation. 
        for frame in frames:
            rgbcontrol.display_frame(tuple(frame))
            now = time.time()
            frame_time = now + 0.010
            while now < frame_time:
                now = time.time()

