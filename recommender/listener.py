import pika



class Listener:
    URL = 'amqp://guest:guest@localhost/'
    QUEUE_NAME = 'rsys'

    def __init__(self, url=URL, cb=None):
        self.connection = pika.BlockingConnection(pika.URLParameters(url))
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







