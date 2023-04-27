from .domain import IRepository, InventoryItem
from .commands import (CheckInItemsToInventory,ChangeMaxQty,RemoveItemsFromInventory,RenameInventoryItem,CreateInventoryItem,DeactivateInventoryItem, Command)
from multipledispatch import dispatch
from .exceptions import GenericError


class InventoryCommandHandlers:
    def __init__(self, repository : IRepository[InventoryItem]) -> None:
        self.__repository = repository

    @dispatch(CreateInventoryItem)
    def _handle(self, message : CreateInventoryItem) -> None:
        item = InventoryItem(message.inventory_item_id, message.name)
        self.__repository.save(item, -1)

    @dispatch(DeactivateInventoryItem)
    def _handle(self, message : DeactivateInventoryItem) -> None:
        item = self.__repository.get_by_id(message.inventory_item_id)
        item.deactivate()
        self.__repository.save(item, message.original_version)

    @dispatch(RemoveItemsFromInventory)
    def _handle(self, message : RemoveItemsFromInventory) -> None:
        item = self.__repository.get_by_id(message.inventory_item_id)
        item.remove(message.count)
        self.__repository.save(item, message.original_version)

    @dispatch(CheckInItemsToInventory)
    def _handle(self, message : CheckInItemsToInventory) -> None:
        item = self.__repository.get_by_id(message.inventory_item_id)
        item.check_in(message.count)
        self.__repository.save(item, message.original_version)

    @dispatch(RenameInventoryItem)
    def _handle(self, message : RenameInventoryItem) -> None:
        item = self.__repository.get_by_id(message.inventory_item_id)
        item.change_name(message.new_name)
        self.__repository.save(item, message.original_version)

    @dispatch(ChangeMaxQty)
    def _handle(self, message : ChangeMaxQty) -> None:
        item = self.__repository.get_by_id(message.inventory_item_id)
        item.change_max_qty(message.new_max_qty)
        self.__repository.save(item, message.original_version)

    def handle(self, message : "Command")  -> None | GenericError:
        try:
            print(message)
            self._handle(message)
        except GenericError as e:
            print(e)
            return e