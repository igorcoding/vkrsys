import rsys
import json
import ConfigParser
import logging

from listener import Listener
from rsys_actions import RsysActions


logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)


def model_initialized_required(f):
    def wrapper(self, *args, **kwargs):
        if self.initialized and self.svd is not None:
            return f(self, *args, **kwargs)
        else:
            return Recommender.error(Responses.MODEL_NOT_INITIALIZED,
                                     'Model is not initialized. Make sure to call /api/init method')

    return wrapper


class ResponseResult:
    def __init__(self, code, status):
        self.code = code
        self.status = status


class Responses:
    OK = ResponseResult(200, 200)
    UNKNOWN_ACTION = ResponseResult(401, 400)
    MODEL_NOT_INITIALIZED = ResponseResult(402, 200)
    PARAMS_UNSATISFIED = ResponseResult(403, 400)
    USER_ITEM_NOT_FOUND = ResponseResult(404, 404)
    PARAMS_NOT_NUMERIC = ResponseResult(405, 400)
    USERS_ITEMS_NOT_AN_ARRAY = ResponseResult(406, 400)

    ONLINE_LEARN_FAILED = ResponseResult(501, 500)
    NO_BACKEND_RESPONSE = ResponseResult(502, 500)

    def __init__(self):
        pass


class Recommender:
    # BROKER_URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'

    def __init__(self):
        # self.listener = Listener(self.BROKER_URL, self.on_message)
        self.users = None
        self.items = None
        self.initialized = False

        self.config = None
        self.svd = None

        self.router = {
            RsysActions.INIT: {
                'params': ['users', 'items'],
                'cb': self.on_init
            },

            RsysActions.RATE: {
                'params': ['user_id', 'item_id', 'rating'],
                'cb': self.on_rate
            },

            RsysActions.USER_ADD: {
                'params': [],
                'cb': self.on_user_add
            },

            RsysActions.ITEM_ADD: {
                'params': [],
                'cb': self.on_item_add
            },
        }

        self.logger = logging.getLogger(Recommender.__name__)

    def _params_checker(self, action, actual):
        absent = []
        required = self.router[action]['params']
        for p in required:
            if p not in actual:
                absent.append(p)

        return absent

    @staticmethod
    def ok(c=Responses.OK):
        return (c.status, {
            'code': c.code
        })

    @staticmethod
    def error(c, msg):
        return (c.status, {
            'code': c.code,
            'msg': msg
        })

    def on_message(self, action, data):
        self.logger.info("Received message: [%s]: %s" % (action, data))
        # d = json.loads(data, encoding='utf-8')

        if action in self.router:
            try:
                absent = self._params_checker(action, data)
                if absent:
                    raise KeyError()

                return self.router[action]['cb'](data)
            except KeyError as e:
                return self.error(Responses.PARAMS_UNSATISFIED,
                                  'Required params are not provided: %s' % self._params_checker(action, data))
        else:
            return self.error(Responses.UNKNOWN_ACTION, "Unknown action provided: %s" % action)

    def on_init(self, data):
        u = json.loads(data['users'], encoding='utf-8')
        i = json.loads(data['items'], encoding='utf-8')

        if type(u) != list or type(i) != list:
            return self.error(Responses.USERS_ITEMS_NOT_AN_ARRAY, 'users and items have to be arrays')

        u = list(set(u))
        i = list(set(i))

        self.users = dict(zip(u, xrange(len(u))))
        self.items = dict(zip(i, xrange(len(i))))

        self.config = rsys.SVDConfig(len(self.users), len(self.items), 0, 4, 0.005)
        self.svd = rsys.SVD(self.config)

        self.initialized = True

        return True

    @model_initialized_required
    def on_user_add(self, data):
        u_id = data['user_id']
        self.users[u_id] = len(self.users)
        self.svd.add_user()

    @model_initialized_required
    def on_item_add(self, data):
        s_id = data['item_id']
        self.items[s_id] = len(self.items)
        self.svd.add_item()

    @model_initialized_required
    def on_rate(self, data):
        try:
            actual_uid = int(data['user_id'])
            actual_iid = int(data['item_id'])
            rating = float(data['rating'])
        except ValueError:
            return self.error(Responses.PARAMS_NOT_NUMERIC, 'Some of params are not numeric')

        try:
            user_id = self.users[actual_uid]
            item_id = self.items[actual_iid]
        except KeyError:
            return self.error(Responses.USER_ITEM_NOT_FOUND, 'This combination of user_id/item_id is not found. '
                                                             'Did you forgot to execute api/add_user or api/add_item?')

        success = self.svd.learn_online(user_id, item_id, rating)

        if success:
            return True
        else:
            return self.error(Responses.ONLINE_LEARN_FAILED,
                              "Couldn't execute an online learning procedure successfully")
