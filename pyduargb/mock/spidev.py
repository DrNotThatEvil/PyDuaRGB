from ..logging import *

logger = get_logger(__file__)


class SpiDev(object):
    """docstring for SpiDev."""
    def __init__(self):
        super(SpiDev, self).__init__()
        self.max_speed_hz = 7800000
        logger.info("Mock spi device initalized")

    def open(self, device, port):
        pass

    def close(self):
        pass

    def xfer(self, data):
        pass
