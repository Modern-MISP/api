from fastapi import APIRouter

from app.schemas.noticelists.noticelist import (
    Noticelist,
)
from app.schemas.noticelists.toggle_enable_noticelist import (
    ToggleEnableNoticelist,
)
from app.schemas.noticelists.update_noticelist import (
    UpdateNoticelist,
)
from app.schemas.noticelists.get_all_noticelist_response import (
    GetAllNoticelist,
)

router = APIRouter(tags=["noticelists"])


@router.get(
    "noticelists/",
    summary="Get all noticelists",
    description="Retrieve a list of all noticelists.",
)
async def get_all_noticelist() -> GetAllNoticelist:
    return None


@router.get(
    "noticelists/view/{noticelistId}",
    deprecated=True,
    summary="Get noticelist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific noticelist by its ID using the old route.",
)
@router.get(
    "/{noticelistId}",
    summary="Get noticelist details",
    description="Retrieve details of a specific noticelist by its ID.",
)
async def get_noticelist(id: int) -> Noticelist:
    return Noticelist()


@router.post(
    "noticelists/toggleEnable/{noticelistId}",
    summary="Disable/Enable noticelist",
    description="Disable/Enable a specific noticelist by its ID.",
)
async def post_toggleEnable(id: int) -> ToggleEnableNoticelist:
    return ToggleEnableNoticelist()


@router.post(
    "noticelists/update",
    deprecated=True,
    summary="Update noticelists (Deprecated)",
    description="Deprecated. Update all noticelists.",
)
@router.put(
    "noticelists/update",
    summary="Update noticelists",
    description="Update all noticelists.",
)
async def update_noticelists() -> UpdateNoticelist:
    return UpdateNoticelist()
