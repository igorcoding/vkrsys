import rsys
import json
import ConfigParser

from listener import Listener


class Recommender:
    BROKER_URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'

    def __init__(self):
        self.listener = Listener(self.BROKER_URL, self.on_message)
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
        self.svd.learn_online(d['user_id'], d['item_id'], d['rating'])
        for i in xrange(0, self.m.rows):
            for j in xrange(0, self.m.cols):
                print "%f " % self.svd.predict(i, j),
            print
        pass

    def start(self):
        print "=== Started Recommender ==="
        self.listener.start()


if __name__ == '__main__':

    r = Recommender()
    r.start()