import socket
import threading

from ..logging import *

logger = get_logger(__file__)


class MasterSlaveSocketThread(threading.Thread):
    ALLOWED_COMMANDS = ['ping', 'quit']

    def __init__(self, client, address):
        super(MasterSlaveSocketThread, self).__init__()
        self._client = client
        self._address = address
        self._stop_event = threading.Event()

    def _send(self, data):
        send_data = b'\x64\x75\x61\x00' + data
        self._client.send(send_data)

    def _recv(self, data):
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
            if comm_str not in self.ALLOWED_COMMANDS:
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

    def _quit(self, extra_data):
        self._client.close()

    def _ping(self, extra_data):
        self._send(b'PONG')

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        # self._client.send(b'INFO')
        while(not self.stopped()):
            if self.stopped():
                break

            try:
                data = self._client.recv(1024)
                if(len(data) > 0):
                    self._recv(data)
            except socket.error:
                continue


class MasterThread(threading.Thread):
    def __init__(self, host, port):
        super(MasterThread, self).__init__()
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))
        self._stop_event = threading.Event()
        self._slave_threads = []

    def stop(self):
        for slave in self._slave_threads:
            slave.stop()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        logging.info("Master/Slave: Master thread started")
        self._sock.listen(5)
        while(not self.stopped()):
            if self.stopped():
                break

            self._sock.settimeout(0.2)
            try:
                client, address = self._sock.accept()
                client.settimeout(60)
                client.setblocking(False)
                slavethread = MasterSlaveSocketThread(client, address)
                slavethread.start()
                self._slave_threads.append(slavethread)
                logging.info("Master/Slave: Connection from slave!")
            except socket.timeout:
                pass
