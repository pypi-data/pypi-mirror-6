#!/usr/bin/env python

import os
import sys

class SerfHandler(object):
    def __init__(self):
        self.name = os.environ['SERF_SELF_NAME']
        self.role = os.environ['SERF_SELF_ROLE']
        if os.environ['SERF_EVENT'] == 'user':
            self.event = os.environ['SERF_USER_EVENT']
        else:
            self.event = os.environ['SERF_EVENT'].replace('-', '_')

    def log(self, message):
        print message

    def run(self, command):
        pass


class SerfHandlerProxy(SerfHandler):

    handlers = {}

    def register(self, role, handler):
        self.handlers[role] = handler

    def get_klass(self):
        klass = False
        if self.role in self.handlers:
            klass = self.handlers[self.role]
        elif 'default' in self.handlers:
            klass = self.handlers['default']
        return klass

    def run(self):
        klass = self.get_klass()
        if not klass:
            self.log("no handler for role")
        else:
            try:
                getattr(klass, self.event)()
            except AttributeError:
                self.log("event not implemented by class")
            except TypeError:
                self.log("no handler for role")


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    handler.register('lb', LbHandler())
    handler.register('web', WebHandler())
    handler.register('default', WebHandler())
    handler.run()
