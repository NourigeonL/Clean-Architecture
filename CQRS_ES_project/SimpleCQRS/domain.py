from __future__ import annotations
import abc
from .guid import Guid
from .events import Event, InventoryItemDeactivated, InventoryItemRenamed,ItemsCheckedInToInventory, ItemsRemovedFromInventory, MaxQtyChanged,InventoryItemCreated
from typing import Sequence, Generic, TypeVar, Type, NewType
from multipledispatch import dispatch
from .event_store import IEventStore
from .exceptions import InvalidOperationError, AggregateNotFoundError

class AggregateRoot(abc.ABC):
    __changes : list[Event] = []
    __version : int
    @property
    @abc.abstractmethod
    def id(self) -> Guid:
        ...

    @property
    def version(self) -> int:
        return self.__version

    def get_uncommitted_changes(self) -> Sequence[Event]:
        return self.__changes

    def mark_changes_as_committed(self) -> None:
        self.__changes.clear()

    def loads_from_history(self, history : Sequence[Event]) -> None:
        for e in history:
            self.__apply_change(e, False)

    # @dispatch(Event)
    @abc.abstractmethod
    def _apply(self, e : "Event") -> None:
        raise NotImplementedError

    def __apply_change(self, event : "Event", is_new : bool) -> None:
        self._apply(event)
        if is_new:
            self.__changes.append(event)

    def _apply_change(self, event : "Event") -> None:
        self.__apply_change(event, True)

class InventoryItem(AggregateRoot):
    __activated : bool
    __id : Guid
    name : str
    available_qty : int = 0
    max_qty : int = 5

    def change_name(self, new_name : str) -> None:
        if not new_name:
            raise ValueError("new_name")
        self._apply_change(InventoryItemRenamed(self.__id,new_name))

    def remove(self, count : int) -> None:
        if count <= 0:
            raise InvalidOperationError("cant remove negative count from inventory")
        self._apply_change(ItemsRemovedFromInventory(self.__id, count))

    def check_in(self, count : int) -> None:
        if count <= 0:
            raise InvalidOperationError("must have a count greater than 0 to add to inventory")
        if self.available_qty + count > self.max_qty:
            raise InvalidOperationError("Checked in count will exceed Max Qty")
        self._apply_change(ItemsCheckedInToInventory(self.__id, count))

    def change_max_qty(self, new_max_qty : int) -> None:
        if new_max_qty <= 0:
            raise InvalidOperationError("New Max Qty must be larger than 0")
        if self.available_qty > new_max_qty:
            raise InvalidOperationError("New Max Qty cannot be less than Available Qty")
        self._apply_change(MaxQtyChanged(self.__id, new_max_qty))

    def deactivate(self):
        if not self.__activated:
            raise InvalidOperationError("already deactivated")
        self._apply_change(InventoryItemDeactivated(self.__id))

    @property
    def id(self):
        return self.__id


    def __init__(self, id : Guid | None = None, name : str | None = None) -> None:
        if id and name:
            self._apply_change(InventoryItemCreated(id, name, self.max_qty))


    @dispatch(InventoryItemCreated)
    def _apply(self : InventoryItem, e : InventoryItemCreated) -> None:
        self.__id = e.id
        self.__activated = True
        self.name = e.name

    @dispatch(InventoryItemDeactivated)
    def _apply(self: InventoryItem, e : InventoryItemDeactivated) -> None:
        self.__activated = False

    @dispatch(MaxQtyChanged)
    def _apply(self: InventoryItem, e : MaxQtyChanged) -> None:
        self.max_qty = e.new_max_qty

    @dispatch(ItemsCheckedInToInventory)
    def _apply(self: InventoryItem, e : ItemsCheckedInToInventory) -> None:
        self.available_qty += e.count

    @dispatch(ItemsRemovedFromInventory)
    def _apply(self: InventoryItem, e : ItemsRemovedFromInventory) -> None:
        self.available_qty -= e.count

    @dispatch(InventoryItemRenamed)
    def _apply(self: InventoryItem, e : InventoryItemRenamed) -> None:
        self.name = e.new_name


T = TypeVar('T', bound=AggregateRoot)

class IRepository(Generic[T], abc.ABC):

 @abc.abstractmethod
 def save(self, aggregate : AggregateRoot, expected_version : int) -> None:
     raise NotImplementedError

 @abc.abstractmethod
 def get_by_id(self, id : Guid) -> T:
     raise NotImplementedError

class Repository(IRepository[T], Generic[T]):
    __storage : IEventStore

    def __init__(self, storage : IEventStore, class_type : Type[T]) -> None:
        self.__storage = storage
        self.class_type = class_type

    def save(self, aggregate : AggregateRoot, expected_version : int) -> None:
        self.__storage.save_events(aggregate.id, aggregate.get_uncommitted_changes(), expected_version)
        aggregate.mark_changes_as_committed()

    def get_by_id(self, id: Guid) -> T:
        obj = self.class_type()
        e = self.__storage.get_events_for_aggregate(id)
        if not e:
            raise AggregateNotFoundError(id)
        obj.loads_from_history(e)
        return obj
