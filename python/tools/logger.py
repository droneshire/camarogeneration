import logging
import os
import sys


FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def get_logger(name, log_file):
    logging.getLoggerClass().user_error = user_error
    logging.basicConfig(level=logging.INFO, filename=os.path.abspath(log_file), format=FORMAT)
    log = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    log.addHandler(handler)
    return log

def user_error(self, msg):
    self.error('USER_ERROR: {}'.format(msg))



