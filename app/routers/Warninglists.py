from fastapi import APIRouter

from app.schemas.warninglists.check_value_warninglists_body import (
    CheckValueWarninglistsBody,
)
from app.schemas.warninglists.check_value_warninglists_response import (
    CheckValueWarninglistsResponse,
)
from app.schemas.warninglists.delete_warninglist_response import (
    DeleteWarninglistResponse,
)
from app.schemas.warninglists.get_selected_all_warninglists_response import (
    GetSelectedAllWarninglistsResponse,
)

from app.schemas.warninglists.get_selected_warninglists_body import (
    GetSelectedWarninglistsBody,
)

from app.schemas.warninglists.toggle_enable_warninglists_body import (
    ToggleEnableWarninglistsBody,
)

from app.schemas.warninglists.toggle_enable_warninglists_response import (
    ToggleEnableWarninglistsResponse,
)
from app.schemas.warninglists.update_all_warninglists_response import (
    UpdateAllWarninglistsResponse,
)

from app.schemas.warninglists.warninglist import Warninglist

from app.schemas.warninglists.create_warninglist_body import (
    CreateWarninglistBody,
)

router = APIRouter(tags=["warninglists"])


@router.get("/warninglists/")
async def get_all_warninglists() -> GetSelectedAllWarninglistsResponse:
    return None


@router.post("/warninglists/")
@router.get("/warninglists?value=String&enabled=boolean")
async def search_warninglists(
    body: GetSelectedWarninglistsBody,
) -> GetSelectedAllWarninglistsResponse:
    return None


@router.get("/warninglists/toggleEnable")
async def post_toggleEnable(
    body: ToggleEnableWarninglistsBody,
) -> ToggleEnableWarninglistsResponse:
    return ToggleEnableWarninglistsBody()


@router.get("/warninglists/view/{warninglistId}")
@router.get("/warningslists/{warninglistId}")
async def view_warninglist(id: int) -> Warninglist:
    return Warninglist()


@router.post("/warninglists/update")
@router.put("/warninglists")
async def update_all_warninglists() -> UpdateAllWarninglistsResponse:
    return UpdateAllWarninglistsResponse()


@router.post("warninglists/new")
async def create_new_warninglist(body: CreateWarninglistBody) -> Warninglist:
    return Warninglist()


@router.delete("warninglists/{id}")
async def delete_warninglist(id: int) -> DeleteWarninglistResponse:
    return DeleteWarninglistResponse()
