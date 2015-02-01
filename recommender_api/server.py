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
from recommender import Recommender, Responses


class ProcessMixin(tornado.web.RequestHandler):

    def start_worker(self, *args, **kwargs):
        res = self.worker(*args, **kwargs)
        self.result_cb(res)
        # POOL = mp.Pool()
        # r = POOL.apply_async(self.worker, args, kwargs, callback=self.result_cb)
        # r.wait()
        # r.wait()
        # POOL.close()
        # POOL.join()

    def _worker(self, *args, **kwargs):
        raise NotImplementedError("Abstract method")

    def _result_cb(self, result):
        raise NotImplementedError("Abstract method")

    def worker(self, *args, **kwargs):
        try:
            return self._worker(*args, **kwargs)
        except tornado.web.HTTPError, e:
            self.set_status(e.status_code)
        except:
            logging.error("_worker problem", exc_info=True)
            self.set_status(500)
        # tornado.ioloop.IOLoop.instance().add_callback(self._result_cb)

    def result_cb(self, result):
        tornado.ioloop.IOLoop.instance().add_callback(self._result_cb, result)


class ApiHandler(ProcessMixin):
    RSYS = Recommender()
    data = None
    res = None

    def _worker(self, *args, **kwargs):
        return self.RSYS.on_message(kwargs['action'], kwargs['data'])
        # self.res = api_executor.execute(ds, self.entity, self.action, self.data)

    def _result_cb(self, result):
        self.res = result
        if hasattr(self, 'res') and self.res is not None:
            if self.res is True:
                self.res = Recommender.ok(Responses.OK)
            self.set_status(self.res[0])
            self.finish(self.res[1])
        elif hasattr(self, 'redir'):
            self.redirect(self.redir)
        else:
            self.res = Recommender.error(Responses.NO_BACKEND_RESPONSE, 'No response from backend methods')
            self.set_status(self.res[0])
            self.finish(self.res[1])

    @tornado.web.asynchronous
    def get(self, action):
        # self.data = parse_get(self.request.arguments)

        data = {}
        args = self.request.arguments
        for arg in args:
            data[arg] = args[arg][0]
        self.start_worker(action=action, data=data)

    # @tornado.web.asynchronous
    # def post(self, action):
    #     # self.data = json.loads(self.request.body, encoding='utf-8')
    #     self.start_worker()


define('port', type=int, default=9001)


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/api(?:/?(\S*))", ApiHandler),
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