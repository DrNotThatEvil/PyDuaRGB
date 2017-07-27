import threading

class AnimationQueueThread(threading.Thread):
    def __init__(self, animation_lock):
        super(AnimationQueueThread, self).__init__()
   
        self.animation_lock = animation_lock
        self._stop_event = threading.Event()

    def _run_stack(self):
        pass

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

            # At this point the tread has the Lock.
            # And can run animations on the AnimationQueue.
    
            print("Test") 
            print("Test.")
            print("Test..")
            self.animation_lock.release()
