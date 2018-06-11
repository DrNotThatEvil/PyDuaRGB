import socket
import threading

from ..logging import *

logger = get_logger(__file__)


class SlaveThread(threading.Thread):
    def __init__(self, host, port):
        super(SlaveThread, self).__init__()
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(60)
        self._sock.connect((host, 8082))
        self._stop_event = threading.Event()
        self._ping_timer = threading.Timer(5.0, self._ping)

    def _send(self, data):
        send_data = b'\x64\x75\x61\x00' + data
        self._sock.send(send_data)

    def _ping(self):
        if not self.stopped():
            self._ping_timer = threading.Timer(5.0, self._ping)
            self._ping_timer.start()

    def stop(self):
        self._send(b'QUIT')

        self._ping_timer.cancel()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self._ping_timer.start()

        while(not self.stopped()):
            if self.stopped():
                break

            try:
                data = self._sock.recv(1024)
                if len(data) > 0:
                    if data == b'PONG':
                        logging.info("PONG RECIEVED")
            except socket.error:
                continue
