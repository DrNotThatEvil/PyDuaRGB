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
        self._led_queue = []

    def get_order(self):
        return self._order

    def get_order_locked(self):
        return self._order_locked

    def get_data(self):
        return self._data

    def add_leds(self, leds):
        self._led_queue.append(leds)

    def pop_leds(self):
        send_array = bytearray()
        if len(self._led_queue) == 0:
            return send_array

        for led in self._led_queue.pop(0):
            send_array.extend(led.get_bytearray(3))
        return send_array


class MasterData(Singleton):
    def __init__(self):
        self._added_leds = 0
        self._continue_slavedata = []

    def _calculate(self):
        self._added_leds = 0
        for sd in self._continue_slavedata:
            sops = sd.get_data()
            if sops['mode'] == 'continue':
                self._added_leds = self._added_leds + sops['leds']

    def write_remote_leds(self, leds):
        # Write the remote leds.
        working_leds = leds
        for sd in self._continue_slavedata:
            data = sd.get_data()
            send_leds = working_leds[:data['leds']]
            sd.add_leds(send_leds)
            working_leds = working_leds[data['leds']:]
            if len(working_leds) == 0:
                break

    def get_send_data(self, hsh):
        for sd in self._continue_slavedata:
            data = sd.get_data()
            if hsh == data['sock_hash']:
                return sd.pop_leds()
        return bytearray(0)

    def get_last_index(self):
        return len(self._continue_slavedata)

    def get_added_leds(self):
        return self._added_leds

    def remove_slave(self, hsh):
        self._continue_slavedata = [
            x for x in self._continue_slavedata
            if not x.get_data()['sock_hash'] == hsh
        ]
        self._calculate()
        print(self._continue_slavedata)
        print("Caluclated size is now: {}".format(self._added_leds))

    def add_slave(self, order, order_locked, data):
        if order in self._continue_slavedata:
            slavedata = self._continue_slavedata[order]
            if order_locked:
                # New order is leading
                if not slavedata.get_order_locked():
                    # At order is not locked we can move it
                    del self._continue_slavedata[order]
                    self._continue_slavedata.insert(order,
                                                    SlaveData(order,
                                                              order_locked,
                                                              data))
                    self._add_slave((slavedata.get_order()+1),
                                    slavedata.get_order_locked(),
                                    SlaveData.get_data())
                else:
                    # Sorry the other data was locked in first.
                    # Lets try to add this slave at the next index.
                    self._add_slave((order+1),
                                    order_locked, data)
        else:
            self._continue_slavedata.insert(order,
                                            SlaveData(order,
                                                      order_locked, data))
            # New data added calculate leds
            self._calculate()
