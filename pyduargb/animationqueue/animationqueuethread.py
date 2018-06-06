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
