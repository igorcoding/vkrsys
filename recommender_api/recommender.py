from pprint import pprint
import rsys
import rsys.exporters
import logging
from db import Db, TableNotCreated

from response import Responses, RespError, R
from util import ok_on_success, model_initialized_required, generate

from rsys_actions import RsysActions


class Recommender:
    def __init__(self):
        self.users = None
        self.items = None
        self.initialized = False

        self.config = None
        self.mysql_conf = None
        self.svd = None
        self.db = Db('../config.conf')

        self.logger = logging.getLogger(Recommender.__name__)

        self.router = {
            RsysActions.RATE: {
                'params': ['user_id', 'item_id', 'rating'],
                'cb': self.on_rate
            },

            RsysActions.LEARN_ONLINE: {
                'params': [],
                'cb': self.on_learn_online
            },

            RsysActions.LEARN_OFFLINE: {
                'params': [],
                'cb': self.on_learn_offline
            },

            RsysActions.RECOMMEND: {
                'params': ['user_id'],
                'cb': self.on_recommend
            }
        }
        self.last_u = None
        self.last_i = None
        self.last_action = None
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

        if data_user_id in self.users:
            return data_user_id
        else:
            raise RespError(Responses.USER_ITEM_NOT_FOUND)

    def _check_item_id(self, data_item_id):
        try:
            data_item_id = int(data_item_id)
        except ValueError:
            raise RespError(Responses.PARAMS_NOT_NUMERIC)

        if data_item_id in self.items:
            return data_item_id
        else:
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

    @staticmethod
    def _cast_to_bool(obj):
        try:
            return bool(obj)
        except ValueError:
            raise RespError(Responses.MALFORMED_REQUEST)

    def initialize(self):
        users = self.db.get_users_ids()
        items = self.db.get_items_ids()
        last_action = self.db.get_last_action()

        self.db.save_lasts(users[-1], items[-1], last_action)
        self.config = rsys.SVDConfig(len(users), len(items), -1, 4, 0.005)
        self.config.set_print_result(False)

        self.config.set_users_ids(users)
        self.config.set_items_ids(items)

        self.mysql_conf = rsys.exporters.SVDMySQLConfig()
        self.mysql_conf.user = self.db.conn_info['user']
        self.mysql_conf.password = self.db.conn_info['passwd']
        self.mysql_conf.db_name = self.db.conn_info['db']
        self.mysql_conf.users_table = "auth_user"
        self.mysql_conf.items_table = "app_song"

        self.config.set_mysql_exporter(self.mysql_conf)
        self.config.set_predictor('sigmoid')

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

    def _prepare(self):
        self.last_u, self.last_i, self.last_action = self.db.get_lasts()
        if self.last_action is None:
            self.last_action = -1
        new_users = self.db.get_users_ids(self.last_u)
        new_items = self.db.get_items_ids(self.last_i)

        last_u = new_users[-1] if len(new_users) > 0 else None
        last_i = new_items[-1] if len(new_items) > 0 else None
        self.db.save_lasts(last_u, last_i, self.last_action)

        self.svd.add_users(new_users)
        self.svd.add_items(new_items)
        self.db.disconnect()

        for u in new_users:
            self.users[u] = 1

        for i in new_items:
            self.items[i] = 1

    @model_initialized_required
    def on_rate(self, data):
        self._prepare()
        user_id = self._check_user_id(data['user_id'])
        item_id = self._check_item_id(data['item_id'])
        rating = self._cast_to_float(data['rating'])

        self.svd.learn_online(user_id, item_id, rating)

    @model_initialized_required
    def on_learn_online(self, data):
        self._prepare()

        def mapper(obj):
            return rsys.ItemScore(obj['user_id'],
                                  obj['item_id'],
                                  obj['rating'])

        actions = self.db.get_user_actions('rate', self.last_action, mapper)
        pprint(actions)
        if len(actions) > 0:
            last_action = actions[-1][0] if len(actions) > 0 else None
            self.db.save_lasts(last_action=last_action)

            scores = [x[1] for x in actions]

            self.svd.learn_online(scores)
            return None

        return R(Responses.OK).em('Nothing to learn')

    @model_initialized_required
    def on_learn_offline(self, data):
        self._prepare()

        # with open('my_data.dat', mode='w') as f:
        #     for s in scores:
        #         f.write("%d::%d::%d::0\n" % (s.user_id, s.item_id, s.score))
        #
        # with open('my_data_users.dat', mode='w') as f:
        #     for u in self.users.keys():
        #         f.write("%d\n" % (u,))
        #
        # with open('my_data_items.dat', mode='w') as f:
        #     for i in self.items.keys():
        #         f.write("%d\n" % (i,))

        mysql_source = \
            rsys.ds.MySQLSource(self.mysql_conf,
                                "SELECT user_id, song_id, rating FROM app_rating ORDER BY user_id, song_id")
        self.svd.learn_offline(mysql_source)

    @model_initialized_required
    def on_recommend(self, data):
        self._prepare()
        user_id = self._check_user_id(data['user_id'])
        return_recs = self._cast_to_bool(data['return_recs']) if 'return_recs' in data else False
        refresh = self._cast_to_bool(data['refresh']) if 'refresh' in data else False
        count = 0

        recs = self.svd.recommend(user_id, count)
        try:
            if refresh:
                self.db.destroy_recommendations(user_id)
            count = self.db.save_recommendations(user_id, recs)
        except TableNotCreated:
            return R(Responses.NOT_OK).em("Couldn't create table.")

        if count > 0:
            r = R(Responses.OK).d({
                'user_id': data['user_id'],
                'count': count
            })

            if return_recs:
                recommendations = map(lambda r: {
                    'item_id': r.item_id,
                    'score': r.score
                }, recs)
                r.data['recommendations'] = recommendations
            return r
        else:
            return R(Responses.NOT_OK).d({
                'user_id': data['user_id']
            }).em('Already have recommendations for this user')