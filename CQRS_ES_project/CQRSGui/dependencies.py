from SimpleCQRS.fake_bus import FakeBus
from SimpleCQRS.event_store import EventStore
from SimpleCQRS.domain import Repository, InventoryItem
from SimpleCQRS.command_handlers import InventoryCommandHandlers
from SimpleCQRS.real_model import InventoryListView, InventoryItemDetailView
from .service_locator import ServiceLocator
from SimpleCQRS.commands import (CreateInventoryItem,ChangeMaxQty,CheckInItemsToInventory,DeactivateInventoryItem,RemoveItemsFromInventory,RenameInventoryItem)
from SimpleCQRS.events import (InventoryItemCreated,InventoryItemDeactivated,InventoryItemRenamed,ItemsCheckedInToInventory,ItemsRemovedFromInventory,MaxQtyChanged)

bus = FakeBus()

storage = EventStore(bus)

rep = Repository[InventoryItem](storage, InventoryItem)

commands_handler = InventoryCommandHandlers(rep)

detail = InventoryItemDetailView()
bus.register_handler(InventoryItemCreated,detail.handle)
bus.register_handler(InventoryItemDeactivated,detail.handle)
bus.register_handler(InventoryItemRenamed,detail.handle)
bus.register_handler(ItemsCheckedInToInventory,detail.handle)
bus.register_handler(ItemsRemovedFromInventory,detail.handle)
bus.register_handler(MaxQtyChanged,detail.handle)
lst = InventoryListView()
bus.register_handler(InventoryItemCreated,lst.handle)
bus.register_handler(InventoryItemDeactivated,lst.handle)
bus.register_handler(InventoryItemRenamed,lst.handle)

ServiceLocator.bus = bus