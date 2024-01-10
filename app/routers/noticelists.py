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


@router.get("noticelists/")
async def get_all_noticelist() -> GetAllNoticelist:
    return None

@router.get("noticelists/view/{noticelistId}")
@router.get("/{noticelistId}")
async def get_noticelist(id: int) -> Noticelist:
    return Noticelist()

@router.post("noticelists/toggleEnable/{noticelistId}")
async def post_toggleEnable(id: int) -> ToggleEnableNoticelist:
    return ToggleEnableNoticelist()

@router.post("noticelists/update")
@router.put("noticelists/update")
async def update_noticelists() -> UpdateNoticelist:
    return UpdateNoticelist()