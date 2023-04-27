from fastapi import APIRouter, Body, status, HTTPException
from fastapi.responses import RedirectResponse
from SimpleCQRS.real_model import ReadModelFacade, InventoryItemDetailsDto, InventoryItemListDto
from typing import Sequence, Annotated
from ..dependencies import ServiceLocator, commands_handler
from SimpleCQRS.guid import Guid, guid
from SimpleCQRS.commands import CreateInventoryItem,ChangeMaxQty,CheckInItemsToInventory,DeactivateInventoryItem,RemoveItemsFromInventory,RenameInventoryItem, Command

router = APIRouter(prefix="/home")

bus = ServiceLocator.bus

read_model = ReadModelFacade()

redirect_response = RedirectResponse(url="/home/", status_code=status.HTTP_301_MOVED_PERMANENTLY)

def process_command(command : "Command") -> RedirectResponse:
    response = commands_handler.handle(command)
    if not response:
        return redirect_response
    raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail=response.json())


@router.get("/", name="index")
async def index() -> Sequence[InventoryItemListDto]:
    return read_model.get_inventory_items()

@router.get("/{id}")
async def details(id : Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)
@router.post("/add/")
async def add(name : Annotated[str, Body()]) -> RedirectResponse:
    return process_command(CreateInventoryItem(guid(), name))

@router.get("/changename/{id}/")
async def change_name(id: Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)

@router.post("/changename/{id}/")
async def change_name(id: Guid, name : Annotated[str, Body()], version : Annotated[int, Body()]) -> RedirectResponse:
    return process_command(RenameInventoryItem(id, name, version))

@router.get("/deactivate/{id}/")
async def deactivate(id: Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)


@router.post("/deactivate/{id}/")
async def deactivate(id: Guid, version : Annotated[int, Body()]) -> RedirectResponse:
    return process_command(DeactivateInventoryItem(id,version))

@router.get("/checkin/{id}/")
async def check_in(id: Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)

@router.post("/checkin/{id}/")
async def check_in(id: Guid,  number : Annotated[int, Body()], version : Annotated[int, Body()]) -> RedirectResponse:
    return process_command(CheckInItemsToInventory(id, number, version))

@router.get("/remove/{id}/")
async def check_in(id: Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)

@router.post("/remove/{id}/")
async def check_in(id: Guid,  number : Annotated[int, Body()], version : Annotated[int, Body()]) -> RedirectResponse:
    return process_command(RemoveItemsFromInventory(id, number, version))

@router.get("/changemaxqty/{id}/")
async def change_max_qty(id: Guid) -> InventoryItemDetailsDto:
    return read_model.get_inventory_item_details(id)

@router.post("/changemaxqty/{id}/")
async def change_max_qty(id: Guid,  number : Annotated[int, Body()], version : Annotated[int, Body()]) -> RedirectResponse:
    return process_command(ChangeMaxQty(id, number, version))