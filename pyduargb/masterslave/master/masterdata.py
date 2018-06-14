import socket
import threading
import select
import json

from enum import Enum

from ...meta import Singleton
from ...logging import *
from ...config import config_system


class SlaveData():
    def __init__(self, order, order_locked, data):
        self._order = order
        self._order_locked = order_locked
        self._data = data

    def get_order(self):
        return self._order

    def get_order_locked(self):
        return self._order_locked

    def get_data(self):
        return self._data


class MasterData(Singleton):
    def __init__(self):
        self._added_leds = 0
        self._slavedata = []

    def _calculate(self):
        self._added_leds = 0
        for sd in self._slavedata:
            sops = sd.get_data()
            if sops['mode'] == 'continue':
                self._added_leds = self._added_leds + sops['leds']

    def write_remote_leds(self, leds):
        # Write the remote leds.
        working_leds = leds
        for sd in self._slavedata:
            data = sd.get_data()
            send_leds = working_leds[:data['leds']]
            working_leds = working_leds[data['leds']]
            print(send_leds)
            # TODO CONTINUE HERE

    def get_last_index(self):
        return len(self._slavedata)

    def get_added_leds(self):
        return len(self._slavedata)

    def add_slave(self, order, order_locked, data):
        if order in self._slavedata:
            slavedata = self._slavedata[order]
            if order_locked:
                # New order is leading
                if not slavedata.get_order_locked():
                    # At order is not locked we can move it
                    del self._slavedata[order]
                    self._slavedata.insert(order,
                                           SlaveData(order,
                                                     order_locked, data))
                    self._add_slave((slavedata.get_order()+1),
                                    slavedata.get_order_locked(),
                                    SlaveData.get_data())
                else:
                    # Sorry the other data was locked in first.
                    # Lets try to add this slave at the next index.
                    self._add_slave((order+1),
                                    order_locked, data)
        else:
            self._slavedata.insert(order,
                                   SlaveData(order, order_locked, data))
            # New data added calculate leds
            self._calculate()
