#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.ioloop
from gottwall.processing import PeriodicProcessor
from gottwall.settings import PERIODIC_PROCESSOR_TIME
from tornado import gen
from tornado.gen import Task


class RedisBackendPeriodicProcessor(PeriodicProcessor):

    def __init__(self, backend, callback_time=None, io_loop=None,
                 tasks_chunk=None, config={}):
        self.backend = backend
        self.config = config
        self.callback_time = int(float(callback_time or self.backend.backend_settings.get('PERIODIC_PROCESSOR_TIME', None) or \
                                 config.get('PERIODIC_PROCESSOR_TIME', PERIODIC_PROCESSOR_TIME)))
        self.io_loop = io_loop or tornado.ioloop.IOLoop.instance()
        self._running = False
        self._timeout = None

    @gen.engine
    def callback(self):
        """Periodic processor callback

        :param application: application instance
        """
        for project in self.config['PROJECTS'].keys():
            (yield Task(self.backend.load_buckets, project))
