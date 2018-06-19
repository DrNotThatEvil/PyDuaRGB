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
    ALLOWED_COMMANDS = ['ping', 'pong', 'quit']

    def __init__(self, host):
        super(MasterSlaveSharedThread, self).__init__()
        self._state = ConnectionState.PRE_CONNECTION
        self._sock = None
        self._host = host
        self._stop_event = threading.Event()
        self._sending = False
        self._send_backlog = {}

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def _ping(self, extra_data, socket):
        logger.info("Ping recieved. Sending pong")
        return b'PONG'

    def _pong(self, extra_data, socket):
        logger.info("Pong recieved")

    def _send_raw(self, data, extra_data, process=False):
        if self._state not in [ConnectionState.LISTENING,
                               ConnectionState.CONNECTED]:
            return

        send_data = b'\x64\x75\x61\x00' + data

        if extra_data is not None:
            send_data = send_data + b'\x00' + extra_data
            # Append nullbyte and extra data to the command

        if not process:
            try:
                return self._sock.send(send_data)
            except socket.error as e:
                return self._error(e)
        return send_data

    def _error(self, error):
        raise NotImplementedError("_error needs to be extended.")

    def _send(self, data, extra_data=None, process=False):
        if extra_data is None:
            return self._send_raw(data, None, process)

        if type(extra_data) is bytes:
            return self._send_raw(data, extra_data, process)

        return self._send_raw(data, extra_data.encode('UTF-8'), process)

    def _recv(self, allowed, data, socket):
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

            return getattr(self, "_{}".format(comm_str))(extra_data, socket)
        except AttributeError as e:
            logger.warning(e)
            logger.warning(
                "slave requested invalid command: {}".format(comm_str)
            )

    def run(self):
        raise NotImplementedError("Run needs to be extended.")
