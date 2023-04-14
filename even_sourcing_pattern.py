import abc
from datetime import datetime
from typing import Dict, List, Tuple, Concatenate,TypeVar, Generic, Any, Type, overload
from functools import singledispatchmethod
import os
from collections.abc import Callable
from dataclasses import dataclass


# Errors

class InvalidDomainError(Exception):
  def __init__(self, message : str, quantity : int, *args: object) -> None:
    self.message = message
    self.quantity = quantity

class InvalidOperationError(Exception):
  def __init__(self, message : int, *args: object) -> None:
    self.message = message
    super().__init__(*args)

# Interface

class IEvent(abc.ABC):
  pass

class ISubscriber(abc.ABC):
  @abc.abstractmethod
  def receive_event(self, event : Type[IEvent])-> None:
    """Receives an event and play it (if needeed) to keep updated the projection"""
    raise NotImplementedError

# Events

class ProductRegistered(IEvent):
  def __init__(self, sku : str , datetime : datetime) -> None:
    self.__sku = sku
    self.__datetime = datetime

  @property
  def sku(self):
    return self.__sku

  @property
  def datetime(self):
    return self.__datetime

class ProductShipped(IEvent):

  def __init__(self, sku : str, quantity : int, datetime : datetime) -> None:
    self.__sku = sku
    self.__quantity = quantity
    self.__datetime = datetime

  @property
  def sku(self):
    return self.__sku

  @property
  def quantity(self):
    return self.__quantity

  @property
  def datetime(self):
    return self.__datetime

class ProductReceived(IEvent):

  def __init__(self, sku : str, quantity : int, datetime : datetime) -> None:
    self.__sku = sku
    self.__quantity = quantity
    self.__datetime = datetime

  @property
  def sku(self):
    return self.__sku

  @property
  def quantity(self):
    return self.__quantity

  @property
  def datetime(self):
    return self.__datetime

class InventoryAdjusted(IEvent):

  def __init__(self, sku : str, quantity : int, reason : str, datetime : datetime) -> None:
    self.__sku = sku
    self.__quantity = quantity
    self.__reason = reason
    self.__datetime = datetime

  @property
  def sku(self):
    return self.__sku

  @property
  def quantity(self):
    return self.__quantity

  @property
  def reason(self):
    return self.__reason

  @property
  def datetime(self):
    return self.__datetime

# Event Sourcing

class WarehouseProduct:
  """Aggregate representing a Product in a Wharehouse"""
  @dataclass
  class CurrentState:
    """Save the current state of the aggregate"""
    quantity_on_hand : int = 0
    registeration_date : datetime | None = None
    sku : str = ""

  def __init__(self) -> None:
    self.__events : List[IEvent] = []
    self.__current_state = self.CurrentState()

  @singledispatchmethod
  def __add_event(self, event) -> None:
    raise InvalidOperationError(message = "Unsupported Event")

  @__add_event.register
  def _(self, event : ProductRegistered) -> None:
    self.__current_state.registeration_date = event.datetime
    self.__current_state.sku = event.sku

  @__add_event.register
  def _(self, event : ProductShipped) -> None:
    self.__current_state.quantity_on_hand -= event.quantity

  @__add_event.register
  def _(self, event : ProductReceived) -> None:
    self.__current_state.quantity_on_hand += event.quantity

  @__add_event.register
  def _(self, event : InventoryAdjusted) -> None:
    self.__current_state.quantity_on_hand += event.quantity

  def add_event(self, event : IEvent) -> None:
    self.__add_event(event)
    self.__events.append(event)

  def get_events(self) -> List[IEvent]:
    return self.__events



  def ship_product(self, quantity : int) -> None:
    if quantity > self.__current_state.quantity_on_hand:
      raise InvalidDomainError(message = "Ah... we don't have enough product to ship?", quantity = quantity)

    self.add_event(ProductShipped(self.sku, quantity, datetime.now()))

  def receive_product(self, quantity : int) -> None:
    self.add_event(ProductReceived(self.sku, quantity, datetime.now()))

  def adjust_inventory(self, quantity : int, reason : str) -> None:
    if self.__current_state.quantity_on_hand + quantity < 0:
      raise InvalidDomainError(message = "Cannot adjust to a new quantity value")
    self.add_event(InventoryAdjusted(self.sku, quantity, reason, datetime.now()))


  @property
  def sku(self):
    return self.__current_state.sku

  @property
  def quantity_on_hand(self):
    return self.__current_state.quantity_on_hand

  @property
  def registeration_date(self):
    return self.__current_state.registeration_date


class WarehouseProductRepository:
  """Repository interacting with an event store"""

  def __init__(self) -> None:
    self.__in_memory_streams : Dict[str, List[IEvent]] = {}
    self.__subscribers : List[ISubscriber] = []


  def get(self, sku : str) -> WarehouseProduct:
    """Retreives the event stream of a wharehouse product and replay its events to get its current state before returning the product"""
    warehouse_product = WarehouseProduct()
    events = self.__in_memory_streams.setdefault(sku,[ProductRegistered(sku, datetime.now())])
    for evnt in events:
      warehouse_product.add_event(evnt)

    return warehouse_product

  def subscribe(self,  subscriber : ISubscriber) -> None:
    self.__subscribers.append(subscriber)

  def notify(self, event : Type[IEvent]):
    for subscriber in self.__subscribers:
      subscriber.receive_event(event)

  def save(self, warehouse_product : WarehouseProduct) -> None:
    """Saves the stream events of the product. Notifies the subscribers with the new events"""
    events = warehouse_product.get_events()
    nb_events = len(events)
    registered_events = self.__in_memory_streams.setdefault(warehouse_product.sku,[])
    nb_registered_events = len(registered_events)
    for i in range(nb_registered_events, nb_events):
      self.notify(events[i])
    self.__in_memory_streams[warehouse_product.sku] = events


# Projection

@dataclass
class Product:
  """Projection of wharehouse product"""
  sku : str
  received : int = 0
  shipped : int = 0
  stored : int = 0
  number_of_time_inventory_adjusted : int = 0

T = TypeVar('T')

class DBContext(Generic[T]):
  __lst_items : List[T] = []
  def add(self, item : T) -> None:
    """add the item to the dabase"""
    self.__lst_items.append(item)

  def get(self, filter : Callable[[T], bool] = lambda x: True) -> T | None:
    """retrieves the first item satifying the condition given."""
    for item in self.__lst_items:
      if filter(item):
        return item
    return None

  def get_all(self, filter : Callable[[T], bool] = lambda x: True) -> List[T]:
    lst = []
    for item in self.__lst_items:
      if filter(item):
        lst.append(item)
    return lst


class ProductRepository(ISubscriber):
  """Repository interacting with a regular store."""

  def __init__(self, products : DBContext[Product]) -> None:
    self.__products = products

  @singledispatchmethod
  def __apply(self, event) -> None:
    return

  @__apply.register
  def _(self, event : ProductShipped) -> None:
    product = self.get_product(event.sku)
    product.shipped += event.quantity
    product.stored -= event.quantity

  @__apply.register
  def _(self, event : ProductReceived) -> None:
    product = self.get_product(event.sku)
    product.received += event.quantity
    product.stored += event.quantity

  @__apply.register
  def _(self, event : InventoryAdjusted) -> None:
    product = self.get_product(event.sku)
    product.stored += event.quantity
    product.number_of_time_inventory_adjusted += 1

  @property
  def products(self):
    return self.__products

  def receive_event(self, event : Type[IEvent]):
    self.__apply(event)

  def get_product(self, sku : str) -> Product:
    """Retrieves a product from the database"""
    product = self.products.get( lambda x : x.sku == sku )
    if product is None:
      product = Product(sku)
      self.products.add(product)
    return product

  def get_all_products(self) -> List[Product]:
    return self.products.get_all()



# Application

def get_quantity() -> Tuple[int, bool]:
  quantity = int(input("> Please enter a quantity : "))
  is_valid = quantity != 0
  return (quantity, is_valid)

def get_reason() -> str:
  return input("> Please enter a reason : ")

def get_sku() -> str:
  return input("> Please enter a Sku : ")


def main():
  warehouse_product_repository = WarehouseProductRepository()
  product_repository = ProductRepository(DBContext[Product]())
  warehouse_product_repository.subscribe(product_repository)
  key = ""
  while key != "X":
    os.system('cls')
    print("R: Receive Inventory")
    print("S: Ship Inventory")
    print("A: Inventory Adjustment")
    print("Q: Quantity On Hand")
    print("E: Events")
    print("P: Projection")
    print("AP: All Projections")
    print("X: Quit")
    key = input("> ").upper()
    if key not in ["R","S","A", "Q", "E", "P", "AP"]:
      continue
    print()
    if key == "AP":
      products = product_repository.get_all_products()
      for product in products:
        print(f"{product.sku} Received: {product.received}, Shipped: {product.shipped}, Stored: {product.stored}, Inventory Adjusted: {product.number_of_time_inventory_adjusted} time(s)")
      input("> OK")
      continue
    sku = get_sku()
    warehouse_product = warehouse_product_repository.get(sku)

    if key == "R":
      quantity, is_valid = get_quantity()
      if is_valid:
        warehouse_product.receive_product(quantity)
        print(f"{sku} Received : {quantity}")
    elif key == "S":
      quantity, is_valid = get_quantity()
      if is_valid:
        try:
          warehouse_product.ship_product(quantity)
          print(f"{sku} Shipped : {quantity}")
        except InvalidDomainError as e:
          print(e.message)
          print(f"Tried to send {e.quantity} of {sku}")

    elif key == "A":
      quantity, is_valid = get_quantity()

      if is_valid:
        reason = get_reason()
        try:
          warehouse_product.adjust_inventory(quantity, reason)
          print(f"{sku} Adjusted: {quantity} {reason}")
        except InvalidDomainError as e:
          print(e.message)
          print(f"Tried to adjust {e.quantity} of {sku}")

    elif key == "Q":
      current_quantity_on_hand = warehouse_product.quantity_on_hand
      print(f"{sku} Quantity On Hand: {current_quantity_on_hand}")

    elif key == "E":
      print(f"{sku} Events:")
      for event in warehouse_product.get_events():
        match event:
          case ProductRegistered():
            print(f"{event.datetime} {sku} Registered")
          case ProductReceived():
            print(f"{event.datetime} {sku} Received: {event.quantity}")
          case ProductShipped():
            print(f"{event.datetime} {sku} Shipped: {event.quantity}")
          case InventoryAdjusted():
            print(f"{event.datetime} {sku} Adjusted: {event.quantity} {event.reason}")

    elif key == "P":
      product = product_repository.get_product(sku)
      print(f"{product.sku} Received: {product.received}, Shipped: {product.shipped}, Stored: {product.stored}, Inventory Adjusted: {product.number_of_time_inventory_adjusted} time(s)")
    warehouse_product_repository.save(warehouse_product)
    input("> OK")




main()
