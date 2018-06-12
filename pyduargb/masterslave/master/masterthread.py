import socket
import threading

from ..masterslaveshared import *
from ...logging import *
from ...config import config_system

logger = get_logger(__file__)


class MasterSlaveSocketThread(MasterSlaveSharedThread):
    ALLOWED_COMMANDS = MasterSlaveSharedThread.ALLOWED_COMMANDS + ['quit']

    def __init__(self, master, client, address, slaveconfig=None):
        super(MasterSlaveSocketThread, self).__init__(address)
        self._state = ConnectionState.CONNECTED
        self._master = master
        self._sock = client
        self._stop_event = threading.Event()

    def _quit(self, extra_data):
        self._sock.close()
        self._master.remove_slave(self)

    def stop(self):
        self._send(b'QUIT')
        self._sock.close()
        self._state = ConnectionState.QUITING
        super(MasterSlaveSocketThread, self).stop()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        # self._client.send(b'INFO')
        while(not self.stopped()):
            if self.stopped():
                break

            try:
                data = self._sock.recv(1024)
                if(len(data) > 0):
                    self._recv(self.ALLOWED_COMMANDS, data)
            except socket.error:
                continue


class MasterThread(MasterSlaveSharedThread):
    def __init__(self, host, port):
        super(MasterThread, self).__init__(host)
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))
        self._slave_threads = []
        self._slave_configs = config_system.ConfigSystem().get_slave_configs()

    def remove_slave(self, slave):
        self._slave_threads.remove(slave)
        logger.info("Slave has disconnected")

    def stop(self):
        self._state = ConnectionState.QUITING
        for index, slave in enumerate(self._slave_threads):
            logger.info("Trying to disconnect slave index: {}".format(index))
            slave.stop()
        super(MasterThread, self).stop()

    def run(self):
        logging.info("Master/Slave: Master thread started")
        self._sock.listen(5)
        self._state = ConnectionState.LISTENING
        while(not self.stopped()):
            if self.stopped():
                break

            self._sock.settimeout(0.2)
            try:
                client, address = self._sock.accept()
                if self._state == ConnectionState.LISTENING:
                    client.settimeout(60)
                    client.setblocking(False)

                    logger.info(self._slave_configs)

                    slavethread = MasterSlaveSocketThread(self,
                                                          client, address)
                    slavethread.start()
                    self._slave_threads.append(slavethread)
                    logging.info("Master/Slave: Connection from slave!")
                else:
                    client.close()
            except socket.timeout:
                pass
