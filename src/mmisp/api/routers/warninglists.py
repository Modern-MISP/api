from fastapi import APIRouter

from ...api_schemas.warninglists.check_value_warninglists_body import (
    CheckValueWarninglistsBody,
)
from ...api_schemas.warninglists.check_value_warninglists_response import (
    CheckValueWarninglistsResponse,
)
from ...api_schemas.warninglists.delete_warninglist_response import (
    DeleteWarninglistResponse,
)
from ...api_schemas.warninglists.get_selected_all_warninglists_response import (
    GetSelectedAllWarninglistsResponse,
)

from ...api_schemas.warninglists.get_selected_warninglists_body import (
    GetSelectedWarninglistsBody,
)

from ...api_schemas.warninglists.toggle_enable_warninglists_body import (
    ToggleEnableWarninglistsBody,
)

from ...api_schemas.warninglists.toggle_enable_warninglists_response import (
    ToggleEnableWarninglistsResponse,
)
from ...api_schemas.warninglists.update_all_warninglists_response import (
    UpdateAllWarninglistsResponse,
)

from ...api_schemas.warninglists.warninglist import Warninglist

from ...api_schemas.warninglists.create_warninglist_body import (
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
    summary="Get selected warninglists (Deprecated)",
    description="Retrieve a list of warninglists, which match given search terms using the old route.",
)
async def search_warninglists(
    body: GetSelectedWarninglistsBody,
) -> GetSelectedAllWarninglistsResponse:
    return None


@router.get(
    "/warninglists?value=String&enabled=boolean",
    summary="Get selected warninglists",
    description="Retrieve a list of warninglists, which match given search terms using the old route.",
)
async def get_warninglists_by_param() -> GetSelectedAllWarninglistsResponse:
    return None


@router.post(
    "/warninglists/toggleEnable",
    summary="Disable/Enable warninglist",
    description="Disable/Enable a specific warninglist by its ID or name.",
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


@router.post(
    "/warninglists/checkValue",
    summary="Get a list of ID and name of warninglists",
    description="Retrieve a list of ID and name of warninglists, which match has the given search term as Entry.",
)
async def get_warninglists_by_value(
    body: CheckValueWarninglistsBody,
) -> CheckValueWarninglistsResponse:
    return CheckValueWarninglistsResponse()


@router.post(
    "/warninglists/update",
    deprecated=True,
    summary="Update warninglists (Deprecated)",
    description="Deprecated. Update all warninglists.",
)
@router.put(
    "/warninglists",
    summary="Update warninglists",
    description="Update all warninglists.",
)
async def update_all_warninglists() -> UpdateAllWarninglistsResponse:
    return UpdateAllWarninglistsResponse()


@router.post(
    "warninglists/new",
    summary="Add a new warninglist",
    description="Add a new warninglist with given details.",
)
async def create_new_warninglist(body: CreateWarninglistBody) -> Warninglist:
    return Warninglist()


@router.delete(
    "warninglists/{id}",
    summary="Delete warninglist",
    description="Delete a specific warninglist.",
)
async def delete_warninglist(id: int) -> DeleteWarninglistResponse:
    return DeleteWarninglistResponse()
