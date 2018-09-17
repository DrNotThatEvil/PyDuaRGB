import socket
import threading
import select
import json
import math
import struct

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
        self._start_queue = {}
        self._frames_queue = {}
        self._frame_pop_count = 0

    def get_order(self):
        return self._order

    def get_order_locked(self):
        return self._order_locked

    def get_data(self):
        return self._data

    def add_frames(self, hsh, frames):
        if hsh not in self._frames_queue:
            self._frames_queue[hsh] = []

        self._frames_queue[hsh].extend(frames)

    def add_start(self, hsh, start, repeat=False):
        self._start_queue[hsh] = {"start":start, "repeat": repeat}

    def add_leds(self, leds):
        self._led_queue.append(leds)

    def get_unsend_length(self, hsh):
        try:
            if hsh not in list(self._frames_queue):
                return 0
            return len(self._frames_queue[hsh])
        except KeyError:
            return 0

    def pop_start(self):
        send_data = bytearray(0) 
        
        if len(self._start_queue) > 0:
            top_queue = list(self._start_queue)[0]
            start = json.dumps(self._start_queue[top_queue]).encode('UTF-8')

            self._start_queue.pop(top_queue)
            send_data = (b'\x3A' + str(top_queue).encode('UTF-8') + b'\x3A' 
                         + start)
   
        return send_data

    def pop_frame(self):
        send_data = bytearray(0) 
         
        if len(self._frames_queue) > 0:
            top_queue = list(self._frames_queue)[0]
            
            max_bytes = 2048
            animation = self._frames_queue[top_queue]
            frame_count = len(animation)
            byte_count = frame_count * 50 * 3
            bytes_divided = math.ceil(byte_count / max_bytes)

            all_frame_bytes = [x for frames in animation for x in frames]
            offset = self._frame_pop_count * math.floor(max_bytes / 3)

            for x in range(math.floor(2048/3)):
                if offset+x >= len(all_frame_bytes):
                    break
                send_data.extend(all_frame_bytes[offset+x].get_bytearray(3))
            
            self._frame_pop_count = self._frame_pop_count + 1
            if self._frame_pop_count > bytes_divided:
                self._frames_queue.pop(top_queue)
                self._frame_pop_count = 0

            send_data = (b'\x3A' + str(top_queue).encode('UTF-8') + b'\x3A' 
                         + send_data)

        return send_data

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

    def get_slave_leds(self, index):
        return self._continue_slavedata[index].get_data()['leds']

    def write_remote_frames(self, index, hsh, slave_frames):
        self._continue_slavedata[index].add_frames(hsh, slave_frames)

    def write_start(self, index, hsh, time, repeat):
        self._continue_slavedata[index].add_start(hsh, time, repeat)

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

    def get_total_unsend_length(self, hsh):
        total = 0
        for sd in self._continue_slavedata:
            total += sd.get_unsend_length(hsh)
        return total

    def get_send_data(self, hsh):
        for sd in self._continue_slavedata:
            data = sd.get_data()
            if hsh == data['sock_hash']:
                return sd.pop_frame()
        return bytearray(0)

    def get_start_send_data(self, hsh):
        for sd in self._continue_slavedata:
            data = sd.get_data()
            if hsh == data['sock_hash']:
                return sd.pop_start()
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
