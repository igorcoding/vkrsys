import pika
import rsys
import json
import ConfigParser


class Listener:
    URL = 'amqp://guest:guest@localhost/'
    QUEUE_NAME = 'rsys'

    def __init__(self, url=URL, cb=None):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.URL))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.QUEUE_NAME, durable=True)
        self.channel.basic_consume(self.callback, queue=self.QUEUE_NAME)
        self.cb = cb

    def start(self):
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.connection.close()
        print 'Closing connection'

    def callback(self, ch, method, properties, body):
        self.cb(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)


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




