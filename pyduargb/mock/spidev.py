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


from ..logging import *

logger = get_logger(__file__)


class SpiDev(object):
    """docstring for SpiDev."""
    def __init__(self):
        super(SpiDev, self).__init__()
        self.max_speed_hz = 7800000
        logger.info("Mock spi device initalized")

    def open(self, device, port):
        pass

    def close(self):
        pass

    def xfer(self, data):
        pass
