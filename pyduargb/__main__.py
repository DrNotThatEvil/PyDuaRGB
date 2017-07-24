from __future__ import print_function, absolute_import, unicode_literals
import os

from .config import config_system
from . import chips
from .rgbcontroller import rgbcontroller
from .animations import pulse

MAIN_CUR_PATH = os.path.dirname(os.path.realpath(__file__))
MAIN_CUR_PATH = os.path.realpath(os.path.join(MAIN_CUR_PATH, '..'))

if __name__ == "__main__":
    configsys = config_system.ConfigSystem(os.path.join(MAIN_CUR_PATH, 'config.ini'))
    chipstr = configsys.get_option('main', 'chiptype')
    chip = chips.CHIP_LOOKUP[chipstr.upper()]()

    rgbcntl = rgbcontroller.RGBController(chip, 50, configsys.get_option('main', 'spidev'))
    rgbcntl.play_animation(1000, pulse.Pulse({'r': 255, 'g':0, 'b':0}))
