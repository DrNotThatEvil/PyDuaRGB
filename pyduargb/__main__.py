from __future__ import print_function, absolute_import, unicode_literals
import os
import threading
import time

from .config import config_system
from . import chips
from .rgbcontroller import rgbcontroller
from .animations import pulse
from .animationqueue.animationqueuethread import AnimationQueueThread
from .animationqueue import *

MAIN_CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_CUR_PATH = os.path.realpath(os.path.join(MAIN_CUR_PATH, '..'))

if __name__ == "__main__":
    configsys = config_system.ConfigSystem(os.path.join(MAIN_CUR_PATH, 'config.ini'))
    chipconfig = configsys.get_option('main', 'chiptype')
    leds = configsys.get_option('main', 'leds')
    spidev = configsys.get_option('main', 'spidev')


    rgbcntl = rgbcontroller.RGBController(chipconfig.get_chip_obj(),
            leds.get_value(),
            spidev.get_str_value()
        )

    animation_lock = threading.RLock()
    animation_thread = AnimationQueueThread(animation_lock)
    
    animation_thread.start()

    animation = pulse.Pulse({'r': 255, 'g': 255, 'b': 255})
    queue = animationqueue.AnimationQueue()
    qi = queueitem.QueueItem(1000, animation, 10, True, False)
    queue.add_queueitem(qi)

    time.sleep(5)

    animation_thread.stop()


    #rgbcntl = rgbcontroller.RGBController(chipconfig.get_chip_obj(), leds.get_value(), spidev.get_str_value())
    #rgbcntl.play_animation(250, pulse.Pulse({'r': 255, 'g':0, 'b':0}))
