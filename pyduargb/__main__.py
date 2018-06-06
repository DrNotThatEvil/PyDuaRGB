from __future__ import print_function, absolute_import, unicode_literals

from werkzeug.serving import run_simple
import os
import threading
import time
import signal
import sys


from .config import config_system
from . import chips
from .rgbcontroller import rgbcontroller
from .animations import pulse
from .animationqueue.animationqueuethread import AnimationQueueThread
from .animationqueue import *
from .jsonserver.jsonrpcserver import *


MAIN_CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_CUR_PATH = os.path.realpath(os.path.join(MAIN_CUR_PATH, '..'))


def main():
    # TODO implement logging in to __main__

    # Gathering config options.
    configsys = config_system.ConfigSystem(
        os.path.join(MAIN_CUR_PATH, 'config.ini')
    )
    chipconfig = configsys.get_option('main', 'chiptype')
    leds = configsys.get_option('main', 'leds')
    spidev = configsys.get_option('main', 'spidev')
    rgbmap = configsys.get_option('main', 'rgbmap')

    # TODO implement checking of all gathered config values

    # Setup RGBController
    rgbcntl = rgbcontroller.RGBController(
        chipconfig.get_chip_obj(),
        leds.get_value(),
        spidev.get_str_value(),
        rgbmap.get_value()
    )

    # Setup AnimationQueue
    queue = animationqueue.AnimationQueue()

    # Setup animation Lock and AnimationQueueThread
    animation_lock = threading.RLock()
    animation_thread = AnimationQueueThread(animation_lock)
    animation_thread.start()

    def signal_handler(signal, frame):
        animation_thread.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Setup json rpc system
    run_simple(
        configsys.get_option('jsonrpc', 'allow').get_value(),
        configsys.get_option('jsonrpc', 'port').get_value(),
        application
    )


if __name__ == "__main__":
    main()
