#!/usr/bin/python
import os
import sys


import functools
import json
import logging
import multiprocessing as mp


import tornado.web
import tornado.gen
from tornado.ioloop import IOLoop
from tornado.options import define, options
from recommender import Recommender, RespError
from response import Responses, RespError, R

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)


class ProcessMixin(tornado.web.RequestHandler):

    def start_worker(self, *args, **kwargs):
        # IOLoop.current().add_future(IOLoop.spawn_callback(lambda: self.worker(*args, **kwargs)),
        #                             lambda f: self.result_cb(*f.result()))
        # pool = ProcessPoolExecutor(max_workers=1)
        req, res = self.worker(*args, **kwargs)
        self.result_cb(req, res)
        # POOL = mp.Pool()
        # r = POOL.apply_async(self.worker, args, kwargs, callback=self.result_cb)
        # r.wait()
        # r.wait()
        # POOL.close()
        # POOL.join()

    def _worker(self, *args, **kwargs):
        raise NotImplementedError("Abstract method")

    def _result_cb(self, req, result):
        raise NotImplementedError("Abstract method")

    def worker(self, *args, **kwargs):
        try:
            # tornado.ioloop.IOLoop.instance().add_callback(self._result_cb)
            return self._worker(*args, **kwargs)
        except tornado.web.HTTPError, e:
            self.set_status(e.status_code)
        except:
            logging.error("_worker problem", exc_info=True)
            self.set_status(500)

    def result_cb(self, req, result):
        tornado.ioloop.IOLoop.instance().add_callback(self._result_cb, req, result)


class ApiHandler(ProcessMixin):
    RSYS = Recommender()
    data = None
    res = None

    def __init__(self, application, request, **kwargs):
        super(ApiHandler, self).__init__(application, request, **kwargs)
        self.logger = logging.getLogger(ApiHandler.__name__)

    def _worker(self, *args, **kwargs):
        req = (kwargs['action'], kwargs['data'])
        try:
            return req, self.RSYS.on_message(*req)
        except RespError as e:
            return req, e.resp
        except Exception as e:
            return req, None

    def _result_cb(self, req, result):
        if result is None:
            self.set_status(500)
            return self.finish("Something went wrong")
        self.res = result.to_res()
        if hasattr(self, 'res') and self.res is not None:
            self.set_status(self.res[0])
            self.finish(self.res[1])
        elif hasattr(self, 'redir'):
            self.redirect(self.redir)
        else:
            self.res = R(Responses.NO_BACKEND_RESPONSE).to_res()
            self.set_status(self.res[0])
            self.finish(self.res[1])
        self.logger.info("Request: %s ===> Response: %s", str(req), str(self.res))

    @tornado.web.asynchronous
    def get(self, action):
        data = {}
        args = self.request.arguments
        for arg in args:
            data[arg] = json.loads(args[arg][0], encoding='utf-8')
        self.start_worker(action=action, data=data)

    @tornado.web.asynchronous
    def post(self, action):
        try:
            data = json.loads(self.request.body, encoding='utf-8')
        except ValueError as e:
            self.res = R(Responses.MALFORMED_REQUEST).to_res()
            self.set_status(self.res[0])
            self.finish(self.res[1])
            return

        self.start_worker(action=action, data=data)


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
        ApiHandler.RSYS.stop()
        logging.info("Server stopped")


if __name__ == "__main__":
    main()