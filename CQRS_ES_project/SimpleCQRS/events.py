from .message import Message
from dataclasses import dataclass
from .guid import Guid, guid





class Event(Message):
    version : int

class InventoryItemDeactivated(Event):
    def __init__(self, id : Guid) -> None:
        self._id = id

    @property
    def id(self)-> Guid:
        return self._id

class InventoryItemCreated(Event):
    def __init__(self, id : Guid, name : str, max_qty : int) -> None:
        self._id = id
        self._name = name
        self._max_qty = max_qty

    @property
    def id(self)-> Guid:
        return self._id

    @property
    def name(self)-> str:
        return self._name

    @property
    def max_qty(self)-> int:
        return self._max_qty


class  InventoryItemRenamed(Event):
    def __init__(self, id : Guid, new_name : str) -> None:
        self._id = id
        self._new_name = new_name

    @property
    def id(self)-> Guid:
        return self._id

    @property
    def new_name(self)-> str:
        return self._new_name

class ItemsCheckedInToInventory(Event):
    def __init__(self, id : Guid, count : int) -> None:
        self._id = id
        self._count = count

    @property
    def id(self)-> Guid:
        return self._id

    @property
    def count(self)-> int:
        return self._count

class ItemsRemovedFromInventory(Event):
    def __init__(self, id : Guid, count : int) -> None:
        self._id = id
        self._count = count

    @property
    def id(self)-> Guid:
        return self._id

    @property
    def count(self)-> int:
        return self._count

class MaxQtyChanged(Event):
    def __init__(self, id : Guid, new_max_qty : int) -> None:
        self._id = id
        self._new_max_qty = new_max_qty

    @property
    def id(self)-> Guid:
        return self._id

    @property
    def new_max_qty(self)-> int:
        return self._new_max_qty