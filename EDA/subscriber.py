import pika, os, sys
from functools import wraps
from typing import Tuple
import threading
import time
import json

class IMessage:
    def __init__(self, message : str) -> None:
        self.message = message


class IEvent(IMessage):
    pass

class OrderPlacedEvent(IEvent):
    pass

class PaymentSuccedEvent(IEvent):
    pass

class ProductShippedEvent(IEvent):
    pass

class ProductRecievedEvent(IEvent):
    pass


class ISubscribe(threading.Thread):
    """Abscract class that correspond to a routine that is executed when recieving a specific type of message. Each instance is run in a thread."""

    def set_routing_key(self,routing_key):
        self._routing_key = routing_key

    def handle(self, event : "IEvent"):
        """The function that is called when a message is read"""
        raise NotImplementedError

    def run(self):
        print(f"{type(self).__name__} is running")
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='events', exchange_type='direct')
        result = channel.queue_declare(queue=type(self).__name__, exclusive=True)

        channel.queue_bind(result.method.queue,
                           exchange="events",
                           routing_key=self._routing_key)

        channel.basic_consume(queue=result.method.queue, on_message_callback=self.handle, auto_ack=True)

        channel.start_consuming()

def subscribe(message_class : type["IMessage"]):
    """Decorator used to subscribe a ISubscribe object to a type of message. For now I didn't find a good way to automatically add the object to the Subscriber.handlers list."""
    def decorator(cl : ISubscribe):
        org_handle = cl.handle

        @wraps(org_handle)
        def wrapper(self, ch, method, properties, body):
            """A lot of argument is send to the callback function when a message is read. However only the body is used. Create a IMessage object corresponding to the type given before sending it to the original function"""
            print("message type :", message_class)
            return org_handle(None, event=message_class(**json.loads(body)))
        cl.handle = wrapper
        return cl
    return decorator

@subscribe(ProductShippedEvent)
class RemoveProduct(ISubscribe):

    def handle(self, event : ProductShippedEvent):
        print(f"Remove product : {event.message}")

@subscribe(ProductRecievedEvent)
class AddProduct(ISubscribe):

    def handle(self, event : ProductRecievedEvent):
        print(f"Add product : {event.message}")

@subscribe(ProductShippedEvent)
class SetProductDisabled(ISubscribe):
    def handle(self, event : ProductShippedEvent):
        print(f"Disable product : {event.message}")


class Subscriber:
    """Contains the list of all subscribers with the type of message they want to listen"""
    handlers : list[Tuple["ISubscribe",type["IEvent"]]] = [(SetProductDisabled(), ProductShippedEvent), (AddProduct(), ProductRecievedEvent), (RemoveProduct(), ProductShippedEvent)]



def main():
    lst_threads : list[threading.Thread] = []

    for sub, event in Subscriber.handlers:
        print(sub, event)

        sub.set_routing_key(event.__name__)
        print("starting thread...")
        sub.start()
        print("adding thread to the list...")
        lst_threads.append(sub)
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

if __name__ == '__main__':
    main()