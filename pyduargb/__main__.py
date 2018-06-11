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
from .master.masterthread import MasterThread
from .slave.slavethread import SlaveThread
from .logging import *


MAIN_CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_CUR_PATH = os.path.realpath(os.path.join(MAIN_CUR_PATH, '..'))
logger = get_logger(__file__)


def main():
    # TODO implement logging in to __main__
    config_file = os.path.join(MAIN_CUR_PATH, 'config.ini')
    if not os.path.isfile(config_file):
        logger.error("Config file not found. Exiting...")
        sys.exit(1)
        return

    # Gathering config options.
    configsys = config_system.ConfigSystem(config_file)

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

    ms_thread = None

    # Setup slave or master networking threads
    if(configsys.get_option('master', 'ip') is not False):
        # instance is slave
        ms_thread = SlaveThread('127.0.0.1', 8083)
    else:
        # instance is a master
        ms_thread = MasterThread('', 8082)
    ms_thread.start()

    # Setup AnimationQueue
    queue = animationqueue.AnimationQueue()

    # Setup animation Lock and AnimationQueueThread
    animation_lock = threading.RLock()
    animation_thread = AnimationQueueThread(animation_lock)
    animation_thread.start()

    def signal_handler(signal, frame):
        ms_thread.stop()
        animation_thread.stop()
        rgbcntl.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Setup json rpc system
    run_simple(
        '127.0.0.1',
        configsys.get_option('jsonrpc', 'port').get_value(),
        application
    )


if __name__ == "__main__":
    main()
