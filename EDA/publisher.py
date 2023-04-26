import pika
import sys, json
from subscriber import (IMessage, IEvent, ProductRecievedEvent, ProductShippedEvent)

message_map = {
    "IMessage" : IMessage,
    "IEvent" : IEvent,
    "ProductRecievedEvent" : ProductRecievedEvent,
    "ProductShippedEvent" : ProductShippedEvent
}


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='events', exchange_type='direct')

event = sys.argv[1] if len(sys.argv) > 1 else 'IMessage'
input_message = ' '.join(sys.argv[2:]) or 'Hello World!'
message_object = message_map[event](input_message)

message = json.dumps(vars(message_object))


channel.basic_publish(
    exchange='events', routing_key=event, body=message)
print(" [x] Sent %r:%r" % (event, message))
connection.close()