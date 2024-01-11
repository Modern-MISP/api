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


@router.get(
    "/warninglists/",
    summary="Get all warninglists",
    description="Retrieve a list of all warninglists.",
)
async def get_all_warninglists() -> GetSelectedAllWarninglistsResponse:
    return None


@router.post(
    "/warninglists/",
    deprecated=True,
    summary="Get selected noticelists (Deprecated)",
    description="Retrieve a list of noticelists, which match given search terms using the old route.",
)
async def search_warninglists(
    body: GetSelectedWarninglistsBody,
) -> GetSelectedAllWarninglistsResponse:
    return None


@router.get(
    "/warninglists?value=String&enabled=boolean",
    summary="Get selected noticelists",
    description="Retrieve a list of noticelists, which match given search terms using the old route.",
)
async def get_warninglists_by_param() -> GetSelectedAllWarninglistsResponse:
    return None


@router.get(
    "/warninglists/toggleEnable",
    summary="Disable/Enable warninglist",
    description="Disable/Enable a specific warninglist by its ID.",
)
async def post_toggleEnable(
    body: ToggleEnableWarninglistsBody,
) -> ToggleEnableWarninglistsResponse:
    return ToggleEnableWarninglistsBody()


@router.get(
    "/warninglists/view/{warninglistId}",
    deprecated=True,
    summary="Get warninglist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific warninglist by its ID using the old route.",
)
@router.get(
    "/warningslists/{warninglistId}",
    summary="Get warninglist details",
    description="Retrieve details of a specific warninglist by its ID.",
)
async def view_warninglist(id: int) -> Warninglist:
    return Warninglist()


@router.post("/warninglists/checkValue")
async def get_warninglists_by_value(
    body: CheckValueWarninglistsBody,
) -> CheckValueWarninglistsResponse:
    return CheckValueWarninglistsResponse()


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
