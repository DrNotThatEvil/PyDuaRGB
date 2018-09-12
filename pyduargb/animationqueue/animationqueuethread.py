import threading

from .animationqueue import AnimationQueue

class AnimationComputeThread(threading.Thread):
    def __init__(self, queueitem):
        super(AnimationComputeThread, self).__init__()
        self._stop_event = threading.Event()
       
        self._queueitem = queueitem

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self._queueitem.calculate_task()

class AnimationQueueThread(threading.Thread):
    MAX_CALC_THREADS = 3
    def __init__(self, animation_lock):
        super(AnimationQueueThread, self).__init__()
   
        self.animation_lock = animation_lock
        self._stop_event = threading.Event()
        self._calc_threads = []

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            if self.stopped():
                break

            queue = AnimationQueue()
            compute_queue = [ x for x in queue.get_queue() 
                              if not x.get_ready() ]
            self._calc_threads = [ x for x in self._calc_threads
                                   if x.is_alive() ]

            for x in compute_queue:
                if (len(self._calc_threads) < 
                        AnimationQueueThread.MAX_CALC_THREADS):
                    calc_thread = AnimationComputeThread(x)
                    calc_thread.start()
                    self._calc_threads.append(calc_thread)
                else:
                    break
                
            if not self.animation_lock.acquire(blocking=False):
                continue
    
            if queue.perform_task():
                queue.item_done()

            self.animation_lock.release()
