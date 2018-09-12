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

from .queueitem import *
from ..logging import *
from ..meta import Singleton


class AnimationQueue(Singleton):
    def __init__(self):
        self._queue = []

    def get_queue(self):
        return self._queue

    def _can_item_be_added(self, queueitem):
        if(len(self._queue) == 0):
            return True

        return self._queue[(len(self._queue)-1)].check_queue_permissions(
            queueitem
        )

    def _should_item_stick(self):
        if(len(self._queue) == 1):
            return self._queue[0].get_sticky()

        return False

    def add_queueitem(self, queueitem):
        if(not isinstance(queueitem, QueueItem)):
            return False

        if(not self._can_item_be_added(queueitem)):
            return False

        self._queue.append(queueitem)
        return True

    def perform_task(self):
        if(len(self._queue) == 0):
            return False

        if not self._queue[0].get_ready():
            return False

        queueitem = self._queue[0]
        logger.info("Starting queueitem...")
        queueitem.perform_task()
        logger.info("Finished queueitem...")

    def item_done(self):
        if(len(self._queue) == 0):
            return

        if(not self._should_item_stick()):
            self._queue.pop(0)

    def get_json_queue(self):
        qi_list = []
        for qi in range(len(self._queue)):
            qi_list.append(self._queue[qi].to_json())
        return qi_list
