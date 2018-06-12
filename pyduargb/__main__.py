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
import argparse
import os
import threading
import time
import signal
import sys

from .config.types import ConfigIpType
from .config import config_system
from . import chips
from .rgbcontroller import rgbcontroller
from .animations import pulse
from .animationqueue.animationqueuethread import AnimationQueueThread
from .animationqueue import *
from .jsonserver.jsonrpcserver import *
from .masterslave.master.masterthread import MasterThread
from .masterslave.slave.slavethread import SlaveThread
from .logging import *


MAIN_CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_CUR_PATH = os.path.realpath(os.path.join(MAIN_CUR_PATH, '..'))
logger = get_logger(__file__)


def parse_arguments():
    description = '''
PyDuaRGB: the python daemon for all your ledstrip needs!
    (c) Willmar 'DrNotThatEvil' Knikker 2018
    Licenced under GNU LGPLv3 (see LICENCE file)
'''

    usage = 'Usage PyDuaRGB.py -h -c CONFIG'

    parser = argparse.ArgumentParser(
            description=description,
            usage=usage,
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--config',
                        help='Specify a config file location',
                        required=False)
    args = vars(parser.parse_args())
    return args


def main():
    args = parse_arguments()

    # TODO implement logging in to __main__
    if args['config'] is None:
        config_file = os.path.join(MAIN_CUR_PATH, 'config.ini')
    else:
        config_file = args['config']

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

    is_slave = (configsys.get_option('master', 'ip') is not False)
    # TODO implement checking of all gathered config values

    # Setup RGBController
    rgbcntl = rgbcontroller.RGBController(
        chipconfig.get_chip_obj(),
        leds.get_value(),
        spidev.get_str_value(),
        rgbmap.get_value(),
        is_slave
    )

    ms_thread = None
    animation_thread = None
    # Setup slave or master networking threads
    if is_slave:
        logger.info("Slave config detected. Starting only slave components.")
        # instance is slave
        ms_thread = SlaveThread(
            configsys.get_option('master', 'ip').get_value()
        )
    else:
        logger.info("Master config detected. Starting all components.")
        # instance is a master
        ms_thread = MasterThread('', 8082)

        # Only masters need a animation queue
        # Setup AnimationQueue
        queue = animationqueue.AnimationQueue()

        # Setup animation Lock and AnimationQueueThread
        animation_lock = threading.RLock()
        animation_thread = AnimationQueueThread(animation_lock)
        animation_thread.start()

    ms_thread.start()

    def signal_handler(signal, frame):
        ms_thread.stop()
        if animation_thread is not None:
            animation_thread.stop()
        rgbcntl.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Setup json rpc system
    # TODO: Decide if this is nesessary for slaves.
    run_simple(
        '0.0.0.0',
        configsys.get_option('jsonrpc', 'port').get_value(),
        application
    )


if __name__ == "__main__":
    main()
