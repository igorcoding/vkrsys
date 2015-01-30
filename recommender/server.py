#!/usr/bin/python
import os
import sys


import functools
import json
import logging
import multiprocessing as mp

import tornado.web
import tornado.gen
import tornado.ioloop
from tornado.options import define, options
from recommender import Recommender


class ProcessMixin(tornado.web.RequestHandler):

    def start_worker(self):
        self.worker()
        self.result_cb(None)
        # POOL = mp.Pool()
        # r = POOL.apply_async(self.worker, callback=self.result_cb)
        # r.wait()
        # r.wait()
        # POOL.close()
        # POOL.join()

    def _worker(self):
        raise NotImplementedError("Abstract method")

    def _result_cb(self):
        raise NotImplementedError("Abstract method")

    def worker(self):
        try:
            self._worker()
        except tornado.web.HTTPError, e:
            self.set_status(e.status_code)
        except:
            logging.error("_worker problem", exc_info=True)
            self.set_status(500)
        # tornado.ioloop.IOLoop.instance().add_callback(self._result_cb)

    def result_cb(self, result):
        tornado.ioloop.IOLoop.instance().add_callback(self._result_cb)


class ApiHandler(ProcessMixin):
    RSYS = Recommender()
    data = None
    res = None

    def _worker(self):
        print self.get_argument('a')
        # self.res = api_executor.execute(ds, self.entity, self.action, self.data)
        self.res = "success, guys!"

    def _result_cb(self):
        if self.get_status() != 200:
            self.send_error(self.get_status())
        elif hasattr(self, 'res') and self.res is not None:
            self.finish(self.res)
        elif hasattr(self, 'redir'):
            self.redirect(self.redir)
        else:
            self.send_error(500)

    @tornado.web.asynchronous
    def get(self, path):
        # self.data = parse_get(self.request.arguments)
        self.start_worker()

    @tornado.web.asynchronous
    def post(self, path):
        # self.data = json.loads(self.request.body, encoding='utf-8')
        self.start_worker()


define('port', type=int, default=9001)


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/api(/?\S*)", ApiHandler),
    ])

    logging.info("Server started on port %s", options.port)
    application.listen(options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        logging.info("Server stopped")


if __name__ == "__main__":
    main()