from .message import Message
from .guid import Guid

class Command(Message):
    pass

class DeactivateInventoryItem(Command):

    def __init__(self, inventory_item_id : Guid, original_version : int) -> None:
        self.__inventory_item_id = inventory_item_id
        self.__original_version = original_version

    @property
    def inventory_item_id(self) -> Guid:
        return self.__inventory_item_id

    @property
    def original_version(self) -> int:
        return self.__original_version


class CreateInventoryItem(Command):
    def __init__(self, inventory_item_id : Guid, name : str) -> None:
        self.__inventory_item_id = inventory_item_id
        self.__name = name

    @property
    def inventory_item_id(self)-> Guid:
        return self.__inventory_item_id

    @property
    def name(self)-> str:
        return self.__name

class  RenameInventoryItem(Command):
    def __init__(self, inventory_item_id : Guid, new_name : str, original_version : int) -> None:
        self.__inventory_item_id = inventory_item_id
        self._new_name = new_name
        self.__original_version = original_version

    @property
    def inventory_item_id(self)-> Guid:
        return self.__inventory_item_id

    @property
    def new_name(self)-> str:
        return self._new_name

    @property
    def original_version(self) -> int:
        return self.__original_version

class CheckInItemsToInventory(Command):
    def __init__(self, inventory_item_id : Guid, count : int, original_version : int) -> None:
        self.__inventory_item_id = inventory_item_id
        self._count = count
        self.__original_version = original_version

    @property
    def inventory_item_id(self)-> Guid:
        return self.__inventory_item_id

    @property
    def count(self)-> int:
        return self._count

    @property
    def original_version(self) -> int:
        return self.__original_version

class RemoveItemsFromInventory(Command):
    def __init__(self, inventory_item_id : Guid, count : int, original_version : int) -> None:
        self.__inventory_item_id = inventory_item_id
        self._count = count
        self.__original_version = original_version

    @property
    def inventory_item_id(self)-> Guid:
        return self.__inventory_item_id

    @property
    def count(self)-> int:
        return self._count

    @property
    def original_version(self) -> int:
        return self.__original_version

class ChangeMaxQty(Command):
    def __init__(self, inventory_item_id : Guid, new_max_qty : int, original_version : int) -> None:
        self.__inventory_item_id = inventory_item_id
        self._new_max_qty = new_max_qty
        self.__original_version = original_version

    @property
    def inventory_item_id(self)-> Guid:
        return self.__inventory_item_id

    @property
    def new_max_qty(self)-> int:
        return self._new_max_qty

    @property
    def original_version(self) -> int:
        return self.__original_version