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


from __future__ import print_function, absolute_import
from os.path import basename
from math import floor
import logging


filenamemap = {
    "config_system.py": "ConfigurationSystem",
    "spidev.py":        "SpiDevice",
    "rgbcontroller.py": "RGBController",
    "__main__.py":      "Core",
    "masterthread.py":  "SlaveMaster",
    "_internal.py":     "Internal Core"
}
longest = len(max(filenamemap.values(), key=len))


def get_logger(filename):
    name = basename(filename)
    if name in filenamemap.keys():
        name = filenamemap[name]

    pad = floor(abs(((longest/2)-(len(name)/2))))
    space = (" " * pad)
    name = "{}{}{}".format(space, name, space)
    extra = {"systemname": name}

    logger = logging.getLogger(filename)
    logger.propagate = False
    syslog = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(systemname)s] [%(levelname)s] %(message)s'
    )
    syslog.setFormatter(formatter)
    syslog.setLevel(logging.DEBUG)
    logger.addHandler(syslog)
    logger.setLevel(logging.DEBUG)

    logger = logging.LoggerAdapter(logger, extra)

    return logger
