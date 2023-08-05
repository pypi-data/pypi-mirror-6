#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from ujson import dumps
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def initialize(self, *args, **kw):
        super(BaseHandler, self).initialize(*args, **kw)

    def on_finish(self):
        if self.application.config.COMMIT_ON_REQUEST_END:
            if self.get_status() > 399:
                logging.debug('ROLLING BACK TRANSACTION')
                self.db.rollback()
            else:
                logging.debug('COMMITTING TRANSACTION')
                self.db.commit()
                self.application.event_bus.flush()

    def options(self):
        self.set_header('Access-Control-Allow-Origin', self.application.config.ORIGIN)
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        self.set_header('Access-Control-Allow-Headers', 'Accept, Content-Type')
        self.set_status(200)
        self.finish()

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', self.application.config.ORIGIN)
        self.set_header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    def write_json(self, obj):
        self.set_header("Content-Type", "application/json")
        self.write(dumps(obj))

    @property
    def db(self):
        return self.application.db
        #if self._session is None:
            #self._session = self.application.get_sqlalchemy_session()

        #return self._session
