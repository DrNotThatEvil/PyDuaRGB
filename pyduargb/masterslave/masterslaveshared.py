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


import socket
import threading
from enum import Enum, IntEnum

from ..animations import Pulse
from ..rgbcontroller import rgbcontroller
from ..logging import *

logger = get_logger(__file__)


class ConnectionState(Enum):
    PRE_CONNECTION = 0
    LISTENING = 1
    CONNECTING = 2
    CONNECTED = 3
    QUITING = 4
    DISCONNECTED = 5


class ClientState(IntEnum):
    WAITING = 0
    MODE_REQUESTED = 1
    RECV = 2
    SEND = 3

# WIP CONTINUE IMPLEMENTING CLIENT STATE 

class MasterSlaveSharedThread(threading.Thread):
    ALLOWED_COMMANDS = ['ping', 'pong', 'quit', 'mode_req', 'mode_ack']

    def __init__(self, host):
        super(MasterSlaveSharedThread, self).__init__()
        self._state = ConnectionState.PRE_CONNECTION
        self._sock = None
        self._host = host
        self._stop_event = threading.Event()
        self._sending = False
        self._send_backlog = {}

        self._remote_state = ClientState.WAITING
        self._host_state = ClientState.WAITING
        self._requested_state = ClientState.WAITING

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def _ping(self, extra_data):
        logger.info("Ping recieved. Sending pong")
        self._send(b'PONG')

    def _pong(self, extra_data):
        logger.info("Pong recieved")

    def _process_backlog(self):
        print(self._send_backlog)

        if len(self._send_backlog) == 0:
            return

        #for hsh, data in self._send_backlog:
        #    print(hsh, data)
            ##self._send_raw(self._send_backlog[hsh][0],
            ##               self._send_backlog[hsh][1])

    def _mode_ack(self, extra_data):
        logger.info("Remote state changed.")
        self._host_state = self._requested_state

    def _mode_req(self, extra_data):
        state_int = int.from_bytes(extra_data, byteorder='little')
        state = ClientState(state_int)

        self._host_state = state
        if state == ClientState.RECV:
            self._remote_state = ClientState.SEND

        if state == ClientState.WAITING:
            self._remote_state = ClientState.WAITING

        logger.info("State changed. {}".format(int(state)))
        self._send_raw(b'MODE_ACK', None, True)

    def _negotiate_state(self, state):
        if (self._remote_state == ClientState.WAITING and
                self._host_state == ClientState.WAITING):
            self._host_state = ClientState.MODE_REQUESTED
            self._remote_state = ClientState.MODE_REQUESTED
            self._requested_state = (ClientState.SEND if state ==
                                     ClientState.RECV
                                     else ClientState.SEND)
            data = int(state).to_bytes(1, byteorder='little')
            self._send_raw(b'MODE_REQ', data, True)

    def _negotiate_reset(self):
        print(self._remote_state)
        print(self._host_state)
        print(self._requested_state)

        if (self._remote_state == ClientState.RECV):
            self._host_state = ClientState.MODE_REQUESTED
            self._remote_state = ClientState.MODE_REQUESTED
            self._requested_state = ClientState.WAITING
            self._send_raw(b'MODE_REQ',
                           int(ClientState.WAITING).to_bytes(
                                1, byteorder='little'), True)

    def _send_raw(self, data, extra_data, negotiate=False):
        if self._state not in [ConnectionState.LISTENING,
                               ConnectionState.CONNECTED]:
            return

        if not negotiate and self._host_state != ClientState.SEND:
            self._negotiate_state(ClientState.RECV)
            request = (data, extra_data)
            if hash(request) not in self._send_backlog.keys():
                self._send_backlog[hash(request)] = request
            return

        send_data = b'\x64\x75\x61\x00' + data

        if extra_data is not None:
            send_data = send_data + b'\x00' + extra_data
            # Append nullbyte and extra data to the command

        self._sock.send(send_data)
        if not negotiate:
            self._negotiate_reset()

    def _send(self, data, extra_data=None, negotiate=False):
        if self._state not in [ConnectionState.LISTENING,
                               ConnectionState.CONNECTED]:
            return

        if not negotiate and self._host_state != ClientState.SEND:
            self._negotiate_state(ClientState.RECV)
            request = (data, (extra_data.encode('UTF-8')
                              if extra_data is not None else None))
            if hash(request) not in self._send_backlog.keys():
                self._send_backlog[hash(request)] = request
            return

        send_data = b'\x64\x75\x61\x00' + data

        if extra_data is not None:
            send_data = send_data + b'\x00' + extra_data.encode('UTF-8')
            # Append nullbyte and extra data to the command

        self._sock.send(send_data)
        if not negotiate:
            self._negotiate_reset()

    def _recv(self, allowed, data):
        if self._state not in [ConnectionState.LISTENING,
                               ConnectionState.CONNECTED]:
            return

        if data[:4] != b'\x64\x75\x61\x00':
            logger.warning("Recieved corrupted data.")
            return

        all_data = data[4:]
        end = all_data.find(b'\x00')
        command = b''
        extra_data = b''

        if end != -1:
            command = all_data[:end]
            extra_data = all_data[(end+1):]
        else:
            command = all_data

        try:
            comm_str = command.decode("utf-8").lower()
            if comm_str not in allowed:
                logger.warning(
                    "command: {} is not allowed.".format(comm_str)
                )
                return

            getattr(self, "_{}".format(comm_str))(extra_data)
        except AttributeError as e:
            logger.warning(e)
            logger.warning(
                "slave requested invalid command: {}".format(comm_str)
            )

    def run(self):
        raise NotImplementedError("Run needs to be extended.")
