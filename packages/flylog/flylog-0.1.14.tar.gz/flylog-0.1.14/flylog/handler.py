# -*- coding: utf-8 -*-

import json
import socket
from logging.handlers import DatagramHandler

from . import constants


class FlyLogHandler(DatagramHandler):
    source = None

    def __init__(self, host=None, port=None, source=None):
        DatagramHandler.__init__(self,
                                 host or constants.AGENT_HOST,
                                 port or constants.AGENT_PORT)
        self.source = source

    def emit(self, record):
        content = self.format(record)
        try:
            s = json.dumps(dict(source=self.source, content=content))
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def makeSocket(self):
        s = DatagramHandler.makeSocket(self)
        # 非阻塞，sendto在缓冲区满的时候也是可能block的
        if s:
            s.setblocking(0)
        return s
