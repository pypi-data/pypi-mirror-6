'''
  @file   BaeLogHandler.py
  @author zhangguanxing (Gethin Zhang) <zhangguanxing01@baidu.com; gethinzhang@gmail.com>
  @date   Wed Sep  4 16:09:46 2013
  
  @brief  BAE distribute log appender
  
  
'''
import time
import traceback
import logging
import sys
import os
from   lib.constants import *

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from   client import Client
from   utils  import *

class BaeLogHandler(logging.Handler):
    def __init__(self, ak, sk, bufcount=CACHE_SHOULD_FLUSH):
        logging.Handler.__init__(self)
        self._client = Client(ak, sk, bufcount)
    
    def flush(self):
        self._client.flush()

    def close(self):
        self._client.close()

    def emit(self, record):
        msg = self.format(record)
        tag = record.name
        if tag == "root":
            tag = None        

        #if exception, set level to warning
        if record.exc_info:
            record.levelno = logging.WARNING

        self._client.log(getbaelevel(record.levelno), msg, record.created * 1000, tag)

    def __del__(self):
        if hasattr(self, "_client"):
            self.close()
