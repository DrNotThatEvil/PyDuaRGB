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


import threading

from .animationqueue import AnimationQueue
from time import sleep


class AnimationQueueThread(threading.Thread):
    def __init__(self, animation_lock):
        super(AnimationQueueThread, self).__init__()

        self.animation_lock = animation_lock
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            if self.stopped():
                break

            if not self.animation_lock.acquire(blocking=False):
                continue

            queue = AnimationQueue()
            queue.perform_task()
            queue.item_done()
            sleep(0.001)

            self.animation_lock.release()
