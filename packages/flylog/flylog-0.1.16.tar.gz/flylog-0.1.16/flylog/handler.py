# -*- coding: utf-8 -*-

import json
import socket
from logging.handlers import DatagramHandler

from . import constants


class FlyLogHandler(DatagramHandler):
    source = None
    source_ip = None

    def __init__(self, host=None, port=None, source=None):
        DatagramHandler.__init__(self,
                                 host or constants.AGENT_HOST,
                                 port or constants.AGENT_PORT)

        # source_ip
        if not self.__class__.source_ip:
            self.__class__.source_ip = socket.gethostbyname(socket.gethostname()) or ''

        self.source = source

    def emit(self, record):
        source = '%s@%s' % (self.source, self.__class__.source_ip)
        content = self.format(record)
        try:
            s = json.dumps(dict(source=source, content=content))
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
