import socket
import threading
import select
import json
import queue
import time

from enum import Enum

from ...logging import *
from ...config import config_system
from ..masterslaveshared import *
from .masterdata import MasterData

logger = get_logger(__file__)
masterdb = MasterData()


class EventThread(threading.Thread):
    def __init__(self, callable):
        super(EventThread, self).__init__()
        self._stop_event = threading.Event()
        self._callable = callable

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            self._callable()

            if not self.stopped():
                time.sleep(5)


class SlaveInfoState(Enum):
    PRE_ASKING = 0
    ASKING = 1
    ASKED = 2


class Slave():
    def __init__(self, config=None):
        self._info_state = SlaveInfoState.PRE_ASKING
        self._info = None
        self._config = config

    def set_info(self, info):
        self._info = info

    def get_info(self):
        return self._info

    def get_config(self):
        return self._config

    def register_in_db(self):
        # Get the last index.
        order = masterdb.get_last_index()
        lock_order = False

        if self._config is not None:
            # we have a id meaning we have a order/slave_id
            order = self._config.get_slave_id()
            lock_order = True
        masterdb.add_slave(order, lock_order, self._info)


class MasterThread(MasterSlaveSharedThread):
    ALLOWED_COMMANDS = (MasterSlaveSharedThread.ALLOWED_COMMANDS +
                        ['quit', 'return_info', 'time_req'])

    def __init__(self, host, port):
        super(MasterThread, self).__init__(host)
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))
        self._slaves_no_info = {}
        self._slaves = {}
        self._message_queues = {}
        self._slave_configs = config_system.ConfigSystem().get_slave_configs()
        self._event_timer = EventThread(self._process_events)
        self._event_timer.start()

    def remove_slave(self, slave):
        self._slave_threads.remove(slave)
        logger.info("Slave has disconnected")

    def stop(self):
        self._event_timer.stop()
        self._state = ConnectionState.QUITING
        # for index, slave in enumerate(self._slave_threads):
        #     logger.info("Trying to disconnect slave index: {}".format(index))
        #     slave.stop()
        super(MasterThread, self).stop()

    def _get_slave_config(self, address):
        for slavecfg in self._slave_configs:
            if slavecfg.get_slave_ip() == address:
                return slavecfg
        return None

    def _quit(self, extra_data, socket):
        logger.info("SlaveX disconnected")
        if socket in self._slaves:
            masterdb.remove_slave(hash(socket))
            del self._slaves[socket]

        if socket in self._readlist:
            self._readlist.remove(socket)
        if socket in self._outputs:
            self._outputs.remove(socket)
        socket.close()
        del self._message_queues[socket]

    def _process_events(self):
        data = self._send(b'INFO', None, True)
        for client in self._slaves_no_info.keys():
            self._message_queues[client].put(data)
            if client not in self._outputs:
                self._outputs.append(client)

    def _time_req(self, extra_data, socket):
        send_time = float(extra_data.decode('UTF-8'))
        data = self._send(b'TIME_RES', json.dumps([send_time, time.time()+6]), 
                          True)
        self._message_queues[socket].put(data)
        if socket not in self._outputs:
            self._outputs.append(socket)

    def _return_info(self, extra_data, socket):
        if socket in self._slaves_no_info:
            slave = self._slaves_no_info[socket]
            del self._slaves_no_info[socket]

            data = json.loads(extra_data.decode('utf-8'))
            mode = 'continue'
            if slave.get_config() is not None:
                mode = slave.get_config().get_slave_mode()

            data['mode'] = mode
            data['sock_hash'] = hash(socket)
            slave.set_info(data)

            self._slaves[socket] = slave
            slave.register_in_db()

            logger.info("SlaveX send info")

    def _process_leds(self):
        for socket in self._slaves.keys():
            led_bytes = masterdb.get_send_data(hash(socket))
            if(len(led_bytes) > 0):
                data = self._send(b'FRAMES', bytes(led_bytes), True)
                self._message_queues[socket].put(data)
                if socket not in self._outputs:
                    self._outputs.append(socket)

    def _error(self, error):
        print(error)

    def run(self):
        logger.info("Started listening to slaves...")
        self._sock.listen(5)
        self._readlist = [self._sock]
        self._outputs = []
        self._state = ConnectionState.LISTENING
        while(not self.stopped()):
            if self.stopped():
                break

            if masterdb.get_added_leds() > 0:
                self._process_leds()

            # client, address = self._sock.accept()
            readable, writable, errored = select.select(self._readlist,
                                                        self._outputs,
                                                        self._readlist, 1)
            for s in readable:
                if s is self._sock:
                    logging.info("Master/Slave: Connection from slave!")
                    client, address = self._sock.accept()
                    if self._state == ConnectionState.LISTENING:
                        client.setsockopt(
                            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                        client.setblocking(False)
                        self._slaves_no_info[client] = Slave(
                            self._get_slave_config(address[0])
                        )
                        self._readlist.append(client)
                        self._outputs.append(client)
                        self._message_queues[client] = queue.Queue()
                    else:
                        client.close()
                    continue

                try:
                    data = s.recv(1)
                    if(len(data) > 0):
                        while b'\x3A' not in data:
                            data += s.recv(1)

                        if self._recv_header(data) is not False:
                            header_data = self._recv_header(data)
                            body = s.recv(header_data[0])

                            resp = self._recv(self.ALLOWED_COMMANDS, body,
                                              header_data[1], s)
                            if resp:
                                data = self._send(resp, None, True)
                                self._message_queues[s].put(data)
                                if s not in self._outputs:
                                    self._outputs.append(s)
                    continue
                except socket.error:
                    pass

            for s in writable:
                try:
                    if s in self._message_queues:
                        next_msg = self._message_queues[s].get_nowait()
                except queue.Empty:
                    self._outputs.remove(s)
                else:
                    try:
                        s.send(next_msg)
                    except socket.error:
                        pass

            for s in errored:
                self._readlist.remove(s)
                if s in self._outputs:
                    self._outputs.remove(s)
                s.close()
                del self._message_queues[s]
