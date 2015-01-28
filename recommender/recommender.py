import rsys
import json
import ConfigParser

from listener import Listener
from rsys_actions import RsysActions


class Recommender:
    BROKER_URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'

    def __init__(self):
        self.listener = Listener(self.BROKER_URL, self.on_message)
        self.users = None
        self.songs = None
        self.initialized = False


        m = rsys.data_sources.matrix(4, 4, -1)
        m.set(0, 0, 4)
        m.set(0, 1, 5)
        m.set(0, 2, 2)
        m.set(0, 3, -1)

        m.set(1, 0, -1)
        m.set(1, 1, 4)
        m.set(1, 2, 4)
        m.set(1, 3, 3)

        m.set(2, 0, -1)
        m.set(2, 1, 2)
        m.set(2, 2, -1)
        m.set(2, 3, -1)

        m.set(3, 0, 5)
        m.set(3, 1, 4)
        m.set(3, 2, -1)
        m.set(3, 3, -1)
        self.m = m

        self.config = rsys.SVDConfig(self.m, 4, 0.05)

        self.svd = rsys.SVD(self.config)
        self.svd.learn()
        for i in xrange(0, m.rows):
            for j in xrange(0, m.cols):
                print "%f " % self.svd.predict(i, j),
            print

    def on_message(self, data):
        print data
        d = json.loads(data, encoding='utf-8')

        action = d['action']
        switcher = {
            RsysActions.INIT: self.on_init,
            RsysActions.RATE: self.on_rate,
            RsysActions.USER_ADD: self.on_user_add,
            RsysActions.SONG_ADD: self.on_song_add,
        }

        if action in switcher:
            switcher[action](d['data'])
        else:
            # TODO
            pass

    def on_init(self, data):
        try:
            u = data['users']
            s = data['songs']
            self.users = dict(zip(u, xrange(len(u))))
            self.songs = dict(zip(s, xrange(len(s))))

            self.initialized = True
        except KeyError:
            # TODO
            pass

    def on_user_add(self, data):
        if self.initialized:
            u_id = data['user_id']
            self.users[u_id] = len(self.users)
            self.svd.add_user()
        else:
            # TODO
            pass

    def on_song_add(self, data):
        if self.initialized:
            s_id = data['song_id']
            self.songs[s_id] = len(self.songs)
            self.svd.add_song()
        else:
            # TODO
            pass

    def on_rate(self, data):
        try:
            self.svd.learn_online(data['user_id'], data['item_id'], data['rating'])
            for i in xrange(0, self.m.rows):
                for j in xrange(0, self.m.cols):
                    print "%f " % self.svd.predict(i, j),
                print
        except KeyError:
            # TODO
            pass

    def start(self):
        print "=== Started Recommender ==="
        self.listener.start()


if __name__ == '__main__':

    r = Recommender()
    r.start()