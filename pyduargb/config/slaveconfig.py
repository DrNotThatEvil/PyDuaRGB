from __future__ import print_function, absolute_import
import os

from .types import *


class SlaveConfig(object):
    def __init__(self, slave_id, slaveip, slaveport):
        self.slave_id = slave_id
        self.slaveip = slaveip
        self.slaveport = slaveport

    def get_slave_id(self):
        return self.slave_id

    def get_slave_ip(self):
        return self.slaveip

    def get_slave_port(self):
        return self.slaveport
