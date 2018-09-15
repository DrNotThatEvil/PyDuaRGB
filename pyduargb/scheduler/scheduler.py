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

from ..masterslave.master.masterdata import MasterData
from ..rgbcontroller import rgbcontroller
from ..logging import *

logger = get_logger(__file__)
masterdb = MasterData()

class Scheduler(object):
    START_DELAY = 5

    def __init__(self):
        pass
    
    def start(self, task):
        # Select a start time.
        # Send start time to slaves
        # Start the animation.

        frames = task.get_frames()

        now = time.time()
        start_time = now + Scheduler.START_DELAY
        logger.debug("Starting item at:{0}".format(start_time))

        # TODO allow this to be stopped.. incase of cntl+c
        while now < start_time:
            now = time.time()
       
        logger.debug("Starting item...")
        rgbcontrol = rgbcontroller.RGBController()

        masterdb.write_remote_frames(0, hash(task), frames)
        # Start the animation. 
        for frame in frames:
            rgbcontrol.display_frame(frame)
