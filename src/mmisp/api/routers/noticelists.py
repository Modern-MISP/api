import json
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.noticelists.get_all_noticelist_response import GetAllNoticelistResponse
from mmisp.api_schemas.noticelists.get_noticelist_response import Data, NoticelistEntryResponse, NoticelistResponse
from mmisp.api_schemas.noticelists.toggle_enable_noticelist_response import ToggleEnableNoticelist
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.db.database import get_db
from mmisp.db.models.noticelist import Noticelist, NoticelistEntry
from mmisp.util.partial import partial
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["noticelists"])


@router.get(
    "/noticelists/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(NoticelistResponse),
    summary="Get noticelist details",
    description="Retrieve details of a specific noticelist by its ID.",
)
async def get_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="noticelistId"),
) -> dict:
    return await _get_noticelist(db, tag_id)


@router.post(
    "/noticelists/toggleEnable/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=partial(ToggleEnableNoticelist),
    summary="Disable/Enable noticelist",
    description="Disable/Enable a specific noticelist by its ID.",
)
async def post_toggleEnable_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    tag_id: str = Path(..., alias="noticelistId"),
) -> dict:
    return await _toggleEnable_noticelists(db, tag_id)


@router.put(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Update noticelists",
    description="Update all noticelists.",
)
async def update_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_noticelists(db, False)


@router.get(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAllNoticelistResponse),
    summary="Get all noticelists",
    description="Retrieve a list of all noticelists.",
)
async def get_all_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_all_noticelists(db)


@router.get(
    "/noticelists/view/{noticelistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(NoticelistResponse),
    summary="Get noticelist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific noticelist by its ID using the old route.",
)
async def get_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: str = Path(..., alias="noticelistId"),
) -> dict:
    return await _get_noticelist(db, noticelist_id)


@router.post(
    "/noticelists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(StandardStatusResponse),
    summary="Update noticelists (Deprecated)",
    description="Deprecated. Update all noticelists.",
)
async def update_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_noticelists(db, True)


# --- endpoint logic ---


async def _get_noticelist(db: Session, noticelist_id: str) -> dict:
    noticelist = check_existence_and_raise(db, Noticelist, noticelist_id, "id", "Noticelist not found")
    noticelist_entries = db.query(NoticelistEntry).filter(NoticelistEntry.noticelist_id == noticelist_id).all()

    return _prepare_noticelist_response(noticelist, noticelist_entries)


async def _toggleEnable_noticelists(db: Session, noticelist_id: str) -> dict:
    noticelist = check_existence_and_raise(db, Noticelist, noticelist_id, "id", "Noticelist not found")
    message = "disabled" if noticelist.enabled else "enabled"

    noticelist.enabled = not noticelist.enabled

    db.commit()

    return ToggleEnableNoticelist(
        saved=True,
        success=True,
        name=f"Noticelist {message}.",
        message=f"Noticelist {message}.",
        url=f"/noticlists/toggleEnable/{noticelist_id}",
        id=noticelist_id,
    )


async def _update_noticelists(db: Session, depr: bool) -> dict:
    number_updated_lists = db.query(Noticelist).count()
    saved = True
    success = True
    name = "Succesfully updated " + str(number_updated_lists) + "noticelists."
    message = "Succesfully updated " + str(number_updated_lists) + "noticelists."
    url = "/noticelists/update" if depr is True else "/noticelists/"

    return StandardStatusResponse(
        saved=saved,
        success=success,
        name=name,
        message=message,
        url=url,
    )


async def _get_all_noticelists(db: Session) -> dict:
    noticelist_data: list[NoticelistResponse] = []
    noticelists = db.query(Noticelist).all()
    for noticelist in noticelists:
        noticelist_entries = db.query(NoticelistEntry).filter(NoticelistEntry.noticelist_id == noticelist.id).all()
        noticelist_data.append(_prepare_noticelist_response(noticelist, noticelist_entries))

    return GetAllNoticelistResponse(response=noticelist_data)


def _prepare_noticelist_entries(noticelist_entries: list[NoticelistEntry]) -> list[NoticelistEntryResponse]:
    noticelist_entry_response = []
    for noticelist_entry in noticelist_entries:
        data = Data(
            scope=json.loads(noticelist_entry.scope),
            field=json.loads(noticelist_entry.field),
            value=json.loads(noticelist_entry.value),
            tags=json.loads(noticelist_entry.tags),
            message=noticelist_entry.message,
        )
        noticelist_entry_response_attribute = NoticelistEntryResponse(
            id=noticelist_entry.id, noticelistId=noticelist_entry.noticelist_id, data=data
        )
        noticelist_entry_response.append(noticelist_entry_response_attribute)

    return noticelist_entry_response


def _prepare_noticelist_response(
    noticelist: Noticelist, noticelist_entries: list[NoticelistEntry]
) -> NoticelistResponse:
    return NoticelistResponse(
        id=noticelist.id,
        name=noticelist.name,
        expanded_name=noticelist.expanded_name,
        ref=json.loads(noticelist.ref),
        geographical_area=json.loads(noticelist.geographical_area),
        version=noticelist.version,
        enabled=noticelist.enabled,
        NoticelistEntry=_prepare_noticelist_entries(noticelist_entries),
    )
