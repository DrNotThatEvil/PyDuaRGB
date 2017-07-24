from __future__ import print_function, absolute_import

from .queueitem import *
from ..meta import Singleton

class Queue(Singleton):
    def __init__(self):
        self._queue = []

    def get_queue(self):
        return self._queue

    def _can_item_be_added(self, queueitem):
        if(len(self._queue) == 0):
            return True

        return self._queue[(len(self._queue)-1)].check_queue_permissions(queueitem)

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

    def item_done(self):
        if(not self._should_item_stick()):
            self._queue.pop()
        
        if(len(self._queue) > 0):
            self._queue[(len(self._queue)-1)].perform_task()
