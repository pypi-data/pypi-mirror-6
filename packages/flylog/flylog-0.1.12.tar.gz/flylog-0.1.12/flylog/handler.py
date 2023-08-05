# -*- coding: utf-8 -*-

import json
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
