import socket
import threading
import sys
import json

from ..masterslaveshared import *
from ...config import config_system
from ...logging import *

logger = get_logger(__file__)


class SlaveThread(MasterSlaveSharedThread):
    ALLOWED_COMMANDS = (MasterSlaveSharedThread.ALLOWED_COMMANDS +
                        ['quit', 'info', 'leds'])

    def __init__(self, host):
        super(SlaveThread, self).__init__(host)
        self._host = host
        self._stop_event = threading.Event()
        self._retrytimer = 2.5
        self._ping_timer = threading.Timer(5.0, self._send_ping)
        self._connection_timer = threading.Timer(
            self._retrytimer, self._connect
        )

        self._connect()

    def _send_ping(self):
        self._send(b'PING')
        if not self.stopped() and self._state == ConnectionState.CONNECTED:
            self._ping_timer = threading.Timer(10.0, self._send_ping)
            self._ping_timer.start()

    def _quit(self, extra_data):
        logger.info("Master disconnected.")
        self._sock.close()
        self._state = ConnectionState.DISCONNECTED

    def _info(self, extra_data):
        logger.info("Info request recieved.")
        configsys = config_system.ConfigSystem()

        self._send(b'RETURN_INFO', extra_data=json.dumps({
            "rgbmap":
                configsys.get_option('main', 'rgbmap').get_value(),
            "chiptype":
                configsys.get_option('main', 'chiptype').get_str_value(),
            "leds":
                configsys.get_option('main', 'leds').get_value()
        }))

    def _connect(self):
        try:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect((self._host, 8082))
                # self._sock.setblocking(False)
                self._sock.settimeout(2)
                self._retrytimer = 2.5
                self._state = ConnectionState.CONNECTED
                self._ping_timer = threading.Timer(
                    10.0, self._send_ping
                )
                self._ping_timer.start()
            except (socket.timeout,
                    ConnectionRefusedError) as e:
                self._sock.close()
                logger.info(
                    "Could not connect to master." +
                    "Retrying after {} seconds".format(self._retrytimer)
                )
                self._state = ConnectionState.DISCONNECTED
                self._retrytimer = self._retrytimer + 2.5
        except KeyboardInterrupt:
            logger.info(
                "Shutting down Slave."
            )
            self.stop()
            sys.exit(0)

    def _leds(self, extra_data):
        bytearr = bytearray(extra_data)
        leds = [[bytearr[(i*3)], bytearr[(i*3)+1], bytearr[(i*3)+2]]
                for i in range(int(len(extra_data)/3))]

    def stop(self):
        if self._state == ConnectionState.CONNECTED:
            self._send(b'QUIT')
            self._state = ConnectionState.QUITING
            self._ping_timer.cancel()

        if self._state == ConnectionState.CONNECTING:
            self._connection_timer.cancel()
        super(SlaveThread, self).stop()

    def run(self):
        while(not self.stopped()):
            if self.stopped():
                break

            if self._state == ConnectionState.DISCONNECTED:
                self._state = ConnectionState.CONNECTING
                self._connection_timer = threading.Timer(
                    self._retrytimer, self._connect
                )
                self._connection_timer.start()
                continue

            if self._state != ConnectionState.CONNECTED:
                continue

            try:
                data = self._sock.recv(1024)
                if(len(data) > 0):
                    self._recv(self.ALLOWED_COMMANDS, data)
                    continue
            except socket.error as e:
                continue

            super(SlaveThread, self)._process_backlog()
