import socket
import threading
import select
import json

from enum import Enum

from ...logging import *
from ...config import config_system
from ..masterslaveshared import *
from .masterdata import MasterData

logger = get_logger(__file__)
masterdb = MasterData()


class SlaveInfoState(Enum):
    PRE_ASKING = 0
    ASKING = 1
    ASKED = 2


class MasterSlaveSocketThread(MasterSlaveSharedThread):
    ALLOWED_COMMANDS = (MasterSlaveSharedThread.ALLOWED_COMMANDS +
                        ['quit', 'return_info'])

    def __init__(self, master, client, address, slaveconfig=None):
        super(MasterSlaveSocketThread, self).__init__(address)
        self._state = ConnectionState.CONNECTED
        self._master = master
        self._sock = client
        self._stop_event = threading.Event()
        self._info = None
        self._info_state = SlaveInfoState.PRE_ASKING
        self._info_timer = threading.Timer(2.0, self._request_info)
        self._info_timer.start()
        self._config = slaveconfig

    def _quit(self, extra_data):
        self._sock.close()
        self._master.remove_slave(self)
        self._state = ConnectionState.QUITING

    def _register_in_db(self):
        # Get the last index.
        order = masterdb.get_last_index()
        lock_order = False

        if self._config is not None:
            # we have a id meaning we have a order/slave_id
            order = self._config.get_slave_id()
            lock_order = True
        masterdb.add_slave(order, lock_order, self._info)

    def _return_info(self, extra_data):
        # TODO replace X with actually assigned order
        logger.info("SlaveX has send his info.")
        self._info_state = SlaveInfoState.ASKED
        self._info_timer.cancel()

        data = json.loads(extra_data.decode('utf-8'))
        mode = 'continue'
        if self._config is not None:
            mode = self._config.get_mode()

        data['mode'] = mode
        self._info = data
        self._register_in_db()
        # TODO save info in singleton

    def _request_info(self):
        if self._info_state == SlaveInfoState.PRE_ASKING:
            self._send(b'INFO')
            self._info_state = SlaveInfoState.ASKING
            self._info_timer = threading.Timer(10.0, self._request_info)
            self._info_timer.start()
        elif self._info_state == SlaveInfoState.ASKING:
            # We still have no info. we need it ask again!
            # TODO Supply slaveid in log
            logger.info("SlaveX Still has not send info. Asking again...")
            self._info_state = SlaveInfoState.PRE_ASKING
            self._info_timer = threading.Timer(2.0, self._request_info)
            self._info_timer.start()

    def stop(self):
        self._info_timer.cancel()
        self._send(b'QUIT')
        self._state = ConnectionState.QUITING
        super(MasterSlaveSocketThread, self).stop()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            if self.stopped() or self._state == ConnectionState.QUITING:
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
        self._slave_sockets = []
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

    def _get_slave_config(self, address):
        for slavecfg in self._slave_configs:
            if slavecfg.get_slave_ip() == address:
                print(address)
        return None

    def run(self):
        logger.info("Started listening to slaves...")
        self._sock.listen(5)
        self._readlist = [self._sock]
        self._state = ConnectionState.LISTENING
        while(not self.stopped()):
            if self.stopped():
                break



            # client, address = self._sock.accept()
            readable, writable, errored = select.select(self._readlist,
                                                        [], [], 1)
            for s in readable:
                if s is not self._sock:
                    continue

                client, address = self._sock.accept()
                if self._state == ConnectionState.LISTENING:
                    client.setblocking(False)
                    slaveconfig = self._get_slave_config(address[0])
                    slavethread = MasterSlaveSocketThread(self,
                                                          client, address,
                                                          slaveconfig)
                    slavethread.start()
                    self._slave_threads.append(slavethread)
                    logging.info("Master/Slave: Connection from slave!")
                else:
                    client.close()
