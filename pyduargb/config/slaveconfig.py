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
import os

from .types import *


class SlaveConfig(object):
    def __init__(self, slave_id, slaveip, mode):
        self.slave_id = slave_id
        self.slaveip = slaveip

    def get_slave_id(self):
        return self.slave_id

    def get_slave_ip(self):
        return self.slaveip

    def get_slave_port(self):
        return self.slaveport
