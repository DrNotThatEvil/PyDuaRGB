import socket
import threading
import sys
import json
import time
import statistics
import struct

from ..masterslaveshared import *
from ...pixel import Pixel
from ...config import config_system
from ...logging import *
from ...scheduler.scheduler import SlaveSchedulerThread, Scheduler

logger = get_logger(__file__)


class SlaveThread(MasterSlaveSharedThread):
    ALLOWED_COMMANDS = (MasterSlaveSharedThread.ALLOWED_COMMANDS +
                        ['quit', 'info', 'frames', 'time_res', 'start'])
    TIMESYNC_MAX_AGE = 30

    def __init__(self, host):
        super(SlaveThread, self).__init__(host)
        self._host = host
        self._stop_event = threading.Event()
        self._retrytimer = 2.5
        self._ping_timer = threading.Timer(5.0, self._send_ping)
        self._connection_timer = threading.Timer(
            self._retrytimer, self._connect
        )

        self._scheduler = Scheduler()
        self._scheduler_thread = SlaveSchedulerThread(self._scheduler)
        self._scheduler_thread.start()

        self._rgbcntl = rgbcontroller.RGBController()
        self._send_info = False
        self._last_sync = 0
        self._sync_step = 0
        self._sync_results = []
        self._incomplete_frame = {}
        self._fullframes = {}

        self._connect()

    def _send_ping(self):
        self._send(b'PING')
        if not self.stopped() and self._state == ConnectionState.CONNECTED:
            self._ping_timer = threading.Timer(10.0, self._send_ping)
            self._ping_timer.start()

    def _quit(self, extra_data, socket):
        logger.info("Master disconnected.")
        self._sock.close()
        self._state = ConnectionState.DISCONNECTED

    def _info(self, extra_data, socket):
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
        self._send_info = True

    def _time_res(self, extra_data, socket):
        time_data = json.loads(extra_data.decode('UTF-8'))
        send_time = time_data[0]
        server_time = time_data[1]
        end = time.time()

        roundtrip = end - send_time
        offset = server_time - end + roundtrip / 2
        result = (roundtrip, offset)
        self._sync_results.append(result)

        if self._sync_step < 5:
            time.sleep(1)
            self._send(b'TIME_REQ', extra_data=str(time.time()))
            self._sync_step = self._sync_step + 1
        else:
            self._calculate_time_sync()
    
    def _calculate_time_sync(self):
        roundtrips = [result[0] for result in self._sync_results]
        limit = statistics.median(roundtrips) + statistics.stdev(roundtrips)

        filtered = [x for x in self._sync_results if x[0] < limit]
        offsets = [x[1] for x in filtered]
       
        self._scheduler.set_offset(sum(offsets) / len(offsets))
        self._sync_results = []

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
                    "Could not connect to master. " +
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

    def _error(self, error):
        self._connection_timer = threading.Timer(
            self._retrytimer, self._connect
        )
        self._connect()

    def _start(self, extra_data, socket):
        header_data = extra_data[1:]

        header_end = header_data.find(b'\x3A')
        header = header_data[:header_end].decode('UTF-8')
        bytearr = bytearray(extra_data[header_end+2:])

        starttime = float(bytearr.decode('UTF-8'))
        frames = self._fullframes[header]

        # TODO Remove old animation when new one is started 

        self._scheduler_thread.add_animation(starttime, frames)


    def _frames(self, extra_data, socket):
        header_data = extra_data[1:]

        header_end = header_data.find(b'\x3A')
        header = header_data[:header_end].decode('utf-8')
        bytearr = bytearray(extra_data[header_end+2:])

        if header not in self._incomplete_frame:
            self._incomplete_frame[header] = []
        
        if header not in self._fullframes:
            self._fullframes[header] = []

        leds = self._incomplete_frame[header]
        leds.extend([[bytearr[(i*3)], bytearr[(i*3)+1], bytearr[(i*3)+2]]
                            for i in range(int(len(bytearr)/3))])

        configsys = config_system.ConfigSystem()
        led_count = configsys.get_option('main', 'leds').get_value()
        all_frames = [leds[x:x+led_count] for x in range(0, len(leds), led_count)]
        unproccesed_frames = [x for x in all_frames if len(x) == led_count]
        processed_frames = [[Pixel({'r': x[0], 'g':x[1], 'b':x[2]}) for x in frame] for frame in unproccesed_frames]

        self._fullframes[header].extend(processed_frames)
        self._incomplete_frame[header] = []
        for frame in all_frames:
            if len(frame) < led_count:
                self._incomplete_frame[header] = frame

    def _leds(self, extra_data, socket):
        bytearr = bytearray(extra_data)
        leds = [[bytearr[(i*3)], bytearr[(i*3)+1], bytearr[(i*3)+2]]
                for i in range(int(len(extra_data)/3))]
        configsys = config_system.ConfigSystem()
        if len(leds) > configsys.get_option('main', 'leds').get_value():
            logger.info("Recieved to many leds")
            return

        self._rgbcntl.process_master_leds(tuple(leds))

    def stop(self):
        self._scheduler_thread.stop()

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

            sync_delta = time.time() - self._last_sync
            if sync_delta > SlaveThread.TIMESYNC_MAX_AGE:
                # START SYNCING 
                self._send(b'TIME_REQ', extra_data=str(time.time()))
                self._sync_step = 0
                self._last_sync = time.time()

            try:
                data = self._sock.recv(1)
                if(len(data) > 0):
                    while b'\x3A' not in data:
                        data += self._sock.recv(1)

                    if self._recv_header(data) is not False:
                        header_data = self._recv_header(data)
                        body = self._sock.recv(header_data[0])
                        self._recv(self.ALLOWED_COMMANDS, body, header_data[1],
                                   self._sock)

                continue
            except socket.error as e:
                continue
