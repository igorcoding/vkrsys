from pprint import pprint
import rsys
import logging

from recommender_api.response import Responses, RespError
from recommender_api.util import ok_on_success, model_initialized_required

from rsys_actions import RsysActions


class Recommender:
    # BROKER_URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'

    def __init__(self):
        # self.listener = Listener(self.BROKER_URL, self.on_message)
        self.users = None
        self.users_arr = None
        self.items = None
        self.items_arr = None
        self.initialized = False

        self.config = None
        self.svd = None

        self.logger = logging.getLogger(Recommender.__name__)

        self.router = {
            RsysActions.INIT: {
                'params': ['users', 'items'],
                'cb': self.on_init
            },

            RsysActions.USER_ADD: {
                'params': ['user_id'],
                'cb': self.on_user_add
            },

            RsysActions.ITEM_ADD: {
                'params': ['item_id'],
                'cb': self.on_item_add
            },

            RsysActions.ITEMS_ADD: {
                'params': ['items'],
                'cb': self.on_items_add
            },

            RsysActions.RATE: {
                'params': ['user_id', 'item_id', 'rating'],
                'cb': self.on_rate
            },

            RsysActions.RATE_BULK: {
                'params': ['scores'],
                'cb': self.on_rate_bulk
            },

            RsysActions.RECOMMEND: {
                'params': ['user_id', 'count'],
                'cb': self.on_recommend
            }
        }

    def _params_checker(self, action, actual):
        absent = []
        required = self.router[action]['params']
        for p in required:
            if p not in actual:
                absent.append(p)

        return absent

    def _get_user_id(self, data_user_id):
        try:
            actual_uid = int(data_user_id)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

        try:
            user_id = self.users[actual_uid]
            return user_id
        except KeyError:
            raise RespError(Responses.USER_ITEM_NOT_FOUND)

    def _get_item_id(self, data_item_id):
        try:
            actual_iid = int(data_item_id)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

        try:
            user_id = self.items[actual_iid]
            return user_id
        except KeyError:
            raise RespError(Responses.USER_ITEM_NOT_FOUND)

    @staticmethod
    def _cast_to_int(obj):
        try:
            return int(obj)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

    @staticmethod
    def _cast_to_float(obj):
        try:
            return float(obj)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

    @ok_on_success
    def on_message(self, action, data):
        self.logger.info("Received message: [%s]: %s" % (action, data))

        if action in self.router:
            try:
                absent = self._params_checker(action, data)
                if absent:
                    raise KeyError()

                return self.router[action]['cb'](data)
            except KeyError as e:
                raise RespError(Responses.PARAMS_UNSATISFIED, str(self._params_checker(action, data)))
        else:
            raise RespError(Responses.UNKNOWN_ACTION, action)

    def on_init(self, data):
        u = data['users']
        i = data['items']

        if type(u) != list or type(i) != list:
            raise RespError(Responses.USERS_ITEMS_NOT_AN_ARRAY)

        u = list(set(u))
        i = list(set(i))
        self.users_arr = u
        self.items_arr = i

        self.users = dict(zip(u, xrange(len(u))))
        self.items = dict(zip(i, xrange(len(i))))

        self.config = rsys.SVDConfig(len(self.users), len(self.items), 0, 4, 0.005)
        self.svd = rsys.SVD(self.config)

        self.initialized = True

    @model_initialized_required
    def on_user_add(self, data):
        u_id = data['user_id']
        self.users[u_id] = len(self.users)
        self.svd.add_user()

    @model_initialized_required
    def on_item_add(self, data):
        i_id = data['item_id']
        self.items[i_id] = len(self.items)
        self.svd.add_item()

    @model_initialized_required
    def on_items_add(self, data):
        items = data['items']

        if type(items) != list:
            return RespError(Responses.USERS_ITEMS_NOT_AN_ARRAY)

        for item_id in items:
            self.items[item_id] = len(self.items)

        self.svd.add_items(len(self.items))

    @model_initialized_required
    def on_rate(self, data):
        user_id = self._get_user_id(data['user_id'])
        item_id = self._get_item_id(data['item_id'])
        rating = self._cast_to_float(data['rating'])

        success = self.svd.learn_online(user_id, item_id, rating)

        if not success:
            raise RespError(Responses.ONLINE_LEARN_FAILED)

    @model_initialized_required
    def on_rate_bulk(self, data):
        data_scores = data['scores']

        if type(data_scores) != list:
            raise RespError(Responses.MALFORMED_REQUEST)

        scores = []
        for s in data_scores:
            user_id = self._get_user_id(s['user_id'])
            item_id = self._get_item_id(s['item_id'])
            rating = self._cast_to_float(data['rating'])

            item_score = rsys.ItemScore(user_id, item_id, rating)
            scores.append(item_score)

        self.svd.learn_online(scores)

    @model_initialized_required
    def on_recommend(self, data):
        user_id = self._get_user_id(data['user_id'])
        count = self._cast_to_int(data['count'])
        recommendations = map(lambda r: {
            'item_id': self.items_arr[r.item_id],
            'score': r.score
        }, self.svd.recommend(user_id, count))
        return Responses.OK.d({
            'user_id': data['user_id'],
            'count': data['count'],
            'recommendations': recommendations
        })