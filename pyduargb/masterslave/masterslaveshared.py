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
from enum import Enum

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


class MasterSlaveSharedThread(threading.Thread):
    ALLOWED_COMMANDS = ['ping', 'pong', 'quit']

    def __init__(self, host):
        super(MasterSlaveSharedThread, self).__init__()
        self._state = ConnectionState.PRE_CONNECTION
        self._sock = None
        self._host = host
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def _ping(self, extra_data):
        logger.info("Ping recieved. Sending pong")
        self._send(b'PONG')

    def _pong(self, extra_data):
        logger.info("Pong recieved")
        rgbcntl = rgbcontroller.RGBController()
        animation = Pulse({'r': 255, 'g': 0, 'b': 0})
        rgbcntl.play_animation(500, animation)

    def _send(self, data, extra_data=None):
        if self._state not in [ConnectionState.LISTENING,
                               ConnectionState.CONNECTED]:
            return

        send_data = b'\x64\x75\x61\x00' + data

        if extra_data is not None:
            send_data = send_data + b'\x00' + extra_data.encode('UTF-8')
            # Append nullbyte and extra data to the command

        self._sock.send(send_data)

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
            extra_data = all_data[end:]
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
        raise NotImplementedError("MasterSlaveSharedThread should be extended")
