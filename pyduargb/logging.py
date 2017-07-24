from __future__ import print_function, absolute_import
import logging

def get_logger(filename):
    logformat = "%(asctime)s [%(levelname)s] %(message)s"
    logger = logging.getLogger(filename)
    logging.basicConfig(format=logformat, level=logging.DEBUG)
    return logger

