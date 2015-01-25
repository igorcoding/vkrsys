import pika

URL = 'amqp://vkmruser:vkmruserpass@localhost/vkmrvhost'
connection = pika.BlockingConnection(pika.URLParameters(URL))
channel = connection.channel()

channel.queue_declare(queue='rsys', durable=True)

msg = 'Hello, World! #%d'

for i in xrange(10):
    m = msg % i
    channel.basic_publish(exchange='',
                          routing_key='rsys',
                          body=m)
    print " [x] Sent '%s'" % m

connection.close()