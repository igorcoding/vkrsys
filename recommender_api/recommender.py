from pprint import pprint
import rsys
import logging
from recommender_api.db import Db

from recommender_api.response import Responses, RespError
from recommender_api.util import ok_on_success, model_initialized_required, generate

from rsys_actions import RsysActions


class Recommender:
    # BROKER_URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'

    def __init__(self):
        # self.listener = Listener(self.BROKER_URL, self.on_message)
        self.users = None
        self.items = None
        self.initialized = False

        self.config = None
        self.svd = None
        self.db = Db('../config.conf')

        self.logger = logging.getLogger(Recommender.__name__)

        self.router = {
            # RsysActions.INIT: {
            # 'params': ['users', 'items'],
            #     'cb': self.on_init
            # },

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
        self.initialize()

    def _params_checker(self, action, actual):
        absent = []
        required = self.router[action]['params']
        for p in required:
            if p not in actual:
                absent.append(p)

        return absent

    def _check_user_id(self, data_user_id):
        try:
            data_user_id = int(data_user_id)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

        try:
            return self.users[data_user_id]
        except KeyError:
            raise RespError(Responses.USER_ITEM_NOT_FOUND)

    def _check_item_id(self, data_item_id):
        try:
            data_item_id = int(data_item_id)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

        try:
            return self.items[data_item_id]
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

    def initialize(self):
        u_count, last_u = self.db.get_users_count()
        s_count, last_s = self.db.get_songs_count()
        self.db.save_lasts(last_u, last_s)
        # TODO: go to db and fetch all factors and load them into self.svd (probably through c++)
        self.config = rsys.SVDConfig(u_count, s_count, 0, 4, 0.005)
        self.config.set_print_result(False)
        users = self.db.get_users_ids()
        items = self.db.get_items_ids()
        self.config.set_users_ids(users)
        self.config.set_items_ids(items)
        self.svd = rsys.SVD(self.config)

        self.users = dict(zip(users, generate(1, len(users))))
        self.items = dict(zip(items, generate(1, len(items))))

        self.initialized = True

        # print last_u, " ", last_s

    def stop(self):
        self.db.disconnect()

    @ok_on_success
    def on_message(self, action, data):
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

    # def on_init(self, data):
    #     u = data['users']
    #     i = data['items']
    #
    #     if type(u) != list or type(i) != list:
    #         raise RespError(Responses.USERS_ITEMS_NOT_AN_ARRAY)
    #
    #     u = list(set(u))
    #     i = list(set(i))
    #     self.users_arr = u
    #     self.items_arr = i
    #
    #     self.users = dict(zip(u, xrange(len(u))))
    #     self.items = dict(zip(i, xrange(len(i))))
    #
    #     self.config = rsys.SVDConfig(len(self.users), len(self.items), 0, 4, 0.005)
    #     self.svd = rsys.SVD(self.config)
    #
    #     self.initialized = True

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
        user_id = self._check_user_id(data['user_id'])
        item_id = self._check_item_id(data['item_id'])
        rating = self._cast_to_float(data['rating'])

        self.svd.learn_online(user_id, item_id, rating)

    @model_initialized_required
    def on_rate_bulk(self, data):
        data_scores = data['scores']

        if type(data_scores) != list:
            raise RespError(Responses.MALFORMED_REQUEST)

        scores = []
        for s in data_scores:
            user_id = self._check_user_id(s['user_id'])
            item_id = self._check_item_id(s['item_id'])
            rating = self._cast_to_float(data['rating'])

            item_score = rsys.ItemScore(user_id, item_id, rating)
            scores.append(item_score)

        self.svd.learn_online(scores)

    @model_initialized_required
    def on_recommend(self, data):
        user_id = self._check_user_id(data['user_id'])
        count = self._cast_to_int(data['count'])
        recommendations = map(lambda r: {
            'item_id': r.item_id,
            'score': r.score
        }, self.svd.recommend(user_id, count))
        return Responses.OK.d({
            'user_id': data['user_id'],
            'count': len(recommendations),
            'recommendations': recommendations
        })