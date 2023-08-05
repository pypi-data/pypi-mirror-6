import os
import sys
import socket
import time

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol  import TBinaryProtocol

from logchain import logchain
from logchain.ttypes import *
from thrift import TSerialization
from logchain.constants import *
from constants import *

class Client:
    def __init__(self, ak, sk, bufcount):
        self._logs  = []
        self._bufcount = bufcount
        self.ak = ak
        self.sk = sk
        self._ok = True
        self._timeout = CLIENT_TIMEOUT
        self._last_flush = time.time()

        if set(("BAE_ENV_LOG_HOST", "BAE_ENV_APPID", "BAE_ENV_LOG_PORT")).issubset(os.environ):
            self._host  = os.environ["BAE_ENV_LOG_HOST"]
            self._appid = os.environ["BAE_ENV_APPID"]
            port  = os.environ["BAE_ENV_LOG_PORT"]
            if not port.isdigit():
                self._ok = False
                raise TypeError("env port error")
            else:
                self._port = int(port)
        else:
            self._ok = False
            msg = "please don't use bae log outside BAE 3.0 environment"
            print >>sys.stderr, msg

        if self._ok:
            self._socket    = TSocket.TSocket(self._host, self._port)
            self._socket.setTimeout(self._timeout)
            self._transport = TTransport.TFramedTransport(self._socket)
            self._protocol  = TBinaryProtocol.TBinaryProtocol(self._transport)
            self._client    = logchain.Client(self._protocol)
        
    def is_open(self):
        if not self._ok:
            return False
        #return self._transport.isOpen()
        return self._socket.isOpen()

    def _check_version(self):
        ret = self._client.check_version(LOGCHAIN_SDK_VERSION)
        if ret == BaeRet.OLD_VERSION:
            print >>sys.stderr, "Warning, you may have an oldversion baelog lib, please update the client version"
        
        
    def open(self):
        if not self._ok:
            return False

        try:
            self._transport.open()
            self._check_version();
        except (TException, TTransport.TTransportException) as e:
            self._timeout = max(self._timeout/2,500)
            self._socket.setTimeout(self._timeout)
            print >>sys.stderr, "send to log server error"
            pass

    def close(self):
        if not self._ok:
            return

        try:
            self.flush()
        except TException:
            pass

        self.flush()
        self._transport.close()

    def flush(self):
        if not self._ok:
            return

        if not self.is_open():
            self.open()

        secret = SecretEntry(self.ak, self.sk)
        log = BaeLog(self._logs, secret)

        ret = BaeRet.RETRY

        try:
            ret = self._client.log(log)
        except (TException, TTransport.TTransportException) as e:
            pass
        except socket.error:
            #BUGFIX: thrift python lib does not handle socket error, so _transport.isOpen will always True
            #I close the transport, so the action will be normal
            self._transport.close()
            
        if ret == BaeRet.OK:
            self._logs = []
            self._last_flush = time.time()
            return
        else:
            if ret == BaeRet.AUTH_FAIL:
                print >>sys.stderr, "log to remote error, please check your ak and sk"

    def should_flush(self):
        if len(self._logs) >= CACHE_SHOULD_DROP:
            self._logs = []
            self._last_flush = time.time()
            return False
        if len(self._logs) >= self._bufcount or time.time() - self._last_flush >= FLUSH_TIMEOUT:
            return True

    def log(self, level, msg, timestamp, tag = None):
        if not self._ok:
            return

        if not self.is_open():
            if not self.open():
                return

        userlog = UserLogEntry()
        
        userlog.appid = self._appid
        userlog.level = level
        if tag and tag != "root":
            userlog.tag = tag
        userlog.timestamp = timestamp
        userlog.msg       = msg

        buf = TSerialization.serialize(userlog)
        
        baelog = BaeLogEntry()
        baelog.category = "user"
        baelog.content  = buf

        self._logs.append(baelog)
        if self.should_flush():
            self.flush()
