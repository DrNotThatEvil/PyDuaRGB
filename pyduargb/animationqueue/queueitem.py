from __future__ import print_function, absolute_import

from .queue import *

class QueueItem(object):
    def __init__(self, animation, runlevel, sticky=False, allow_lower_runlevel=False):
        self.animation = animation
        self.runlevel = runlevel
        self.sticky = sticky
        self.allow_lower_runlevel = allow_lower_runlevel 

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
        queue = Queue()
        #animation.display()
        queue.item_done() 
