import threading
import socket
from ..logging import *

logger = get_logger(__file__)

class SlaveConnection(threading.Thread):
    def __init__(self, client, addr):
        super(SlaveConnection, self).__init__()

        self._client = client
        self._client.setblocking(0)
        self._client.settimeout(5)
        self._addr = addr
        self._stop_event = threading.Event()

    def stop(self):
        self._client.close()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while(not self.stopped()):
            if self.stopped():
                break

            try:
                data = self._client.recv(4096)
                response = "Echo: " + data.decode() 
                self._client.send(response.encode())
            except:
                pass

class MasterSlaveThread(threading.Thread):
    def __init__(self, host, port):
        super(MasterSlaveThread, self).__init__()
        self._host = host
        self._port = port
        self._sock = socket.socket()

        self._sock.bind((self._host, self._port))
        self._sock.setblocking(0)
        self._sock.settimeout(5)

        self._stop_event = threading.Event()
        self._slave_threads = []

    def stop(self):
        for thread in self._slave_threads:
            logger.debug("Fuck it coool ")
            thread.stop()

        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self._sock.listen(5)
        while(not self.stopped()):
            if self.stopped():
                break
            
            try:
                c, addr = self._sock.accept()
                logger.debug("Connection recieved. Starting slave connection")
                connection = SlaveConnection(c, addr)
                self._slave_threads.append(connection)
                connection.start()
            except:
                pass
            
