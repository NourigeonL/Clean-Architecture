import abc
from typing import Sequence, Callable, ParamSpec, Generic, TypeVar
from .guid import Guid
from dataclasses import dataclass
from .events import (InventoryItemCreated, InventoryItemRenamed, InventoryItemDeactivated, ItemsCheckedInToInventory, ItemsRemovedFromInventory, MaxQtyChanged)
from multipledispatch import dispatch
from .exceptions import InvalidOperationError
from .message import Message
from pydantic import BaseModel


T = TypeVar('T', bound=Message, contravariant=True)
P = ParamSpec('P')

class Handles(Generic[T], abc.ABC):

    @abc.abstractmethod
    def handle(self, message : T)-> None:
        raise NotImplementedError

@dataclass
class InventoryItemDetailsDto:
    id : Guid
    name : str
    max_qty : int
    current_count : int
    version : int

@dataclass
class InventoryItemListDto:
    id : Guid
    name : str

class FakeDatabase:
    details : dict[Guid, InventoryItemDetailsDto] = {}
    lst : list[InventoryItemListDto] = []

    @staticmethod
    def find(filter : Callable[[InventoryItemListDto],bool]= lambda x: True) -> InventoryItemListDto | None:
        for item in FakeDatabase.lst:
            if filter(item):
                return item
        return None

    @staticmethod
    def remove_all(filter : Callable[[InventoryItemListDto],bool]= lambda x: True) -> InventoryItemListDto:
        item = FakeDatabase.find(filter)
        while item:
            FakeDatabase.lst.remove(item)
            item = FakeDatabase.find(filter)


class IReadModelFacade(abc.ABC):

    @abc.abstractmethod
    def get_inventory_items(self) -> Sequence[InventoryItemListDto]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_inventory_item_details(self, id : Guid) -> InventoryItemDetailsDto:
        raise NotImplementedError

class ReadModelFacade(IReadModelFacade):
    def get_inventory_items(self) -> Sequence[InventoryItemListDto]:
        return FakeDatabase.lst

    def get_inventory_item_details(self, id: Guid) -> InventoryItemDetailsDto:
        return FakeDatabase.details[id]


class InventoryListView(Handles):

    @dispatch(InventoryItemCreated)
    def handle(self, message: InventoryItemCreated) -> None:
        FakeDatabase.lst.append(InventoryItemListDto(message.id, message.name))

    @dispatch(InventoryItemRenamed)
    def handle(self, message: InventoryItemRenamed) -> None:
        item = FakeDatabase.find(lambda x : x.id == message.id)
        item.name = message.new_name

    @dispatch(InventoryItemDeactivated)
    def handle(self, message: InventoryItemDeactivated) -> None:
        FakeDatabase.remove_all(lambda x : x.id == message.id)

class InventoryItemDetailView(Handles):

    @dispatch(InventoryItemCreated)
    def handle(self, message: InventoryItemCreated) -> None:
        print("InventoryItemDetailView called")
        FakeDatabase.details[message.id] = InventoryItemDetailsDto(message.id, message.name, message.max_qty, 0, 0)

    def __get_details_item(self, id : Guid) -> InventoryItemDetailsDto:
        d = FakeDatabase.details.get(id)
        if not d:
            raise InvalidOperationError("did not find the original inventory this shouldnt happen")
        return d

    @dispatch(InventoryItemRenamed)
    def handle(self, message: InventoryItemRenamed) -> None:
        d = self.__get_details_item(message.id)
        d.name = message.new_name
        d.version = message.version

    @dispatch(ItemsRemovedFromInventory)
    def handle(self, message: ItemsRemovedFromInventory) -> None:
        d = self.__get_details_item(message.id)
        d.current_count -= message.count
        d.version = message.version

    @dispatch(ItemsCheckedInToInventory)
    def handle(self, message: ItemsCheckedInToInventory) -> None:
        d = self.__get_details_item(message.id)
        d.current_count += message.count
        d.version = message.version

    @dispatch(InventoryItemDeactivated)
    def handle(self, message: InventoryItemDeactivated) -> None:
        FakeDatabase.details.pop(message.id)

    @dispatch(MaxQtyChanged)
    def handle(self, message: MaxQtyChanged) -> None:
        d = self.__get_details_item(message.id)
        d.max_qty = message.new_max_qty
        d.version = message.version
