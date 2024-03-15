import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.noticelists.get_all_noticelist_response import GetAllNoticelist, GetAllNoticelistResponse
from mmisp.api_schemas.noticelists.get_noticelist_response import (
    NoticelistAttributes,
    NoticelistAttributesResponse,
    NoticelistEntryResponse,
    NoticelistResponse,
)
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse, StandardStatusResponse
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.noticelist import Noticelist, NoticelistEntry
from mmisp.util.partial import partial

router = APIRouter(tags=["noticelists"])


@router.get(
    "/noticelists/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=NoticelistResponse,
    summary="Get noticelist details",
    description="Retrieve details of a specific noticelist by its ID.",
)
@with_session_management
async def get_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> NoticelistResponse:
    return await _get_noticelist(db, noticelist_id)


@router.post(
    "/noticelists/toggleEnable/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusIdentifiedResponse,
    summary="Disable/Enable noticelist",
    description="Disable/Enable a specific noticelist by its ID.",
)
@with_session_management
async def post_toggleEnable_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> StandardStatusIdentifiedResponse:
    return await _toggleEnable_noticelists(db, noticelist_id)


@router.put(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update noticelists",
    description="Update all noticelists.",
)
@with_session_management
async def update_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    return await _update_noticelists(db, False)


@router.get(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetAllNoticelistResponse),
    summary="Get all noticelists",
    description="Retrieve a list of all noticelists.",
)
@with_session_management
async def get_all_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_all_noticelists(db)


# --- deprecated ---


@router.get(
    "/noticelists/view/{noticelistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=NoticelistResponse,
    summary="Get noticelist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific noticelist by its ID using the old route.",
)
@with_session_management
async def get_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> NoticelistResponse:
    return await _get_noticelist(db, noticelist_id)


@router.post(
    "/noticelists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update noticelists (Deprecated)",
    description="Deprecated. Update all noticelists.",
)
@with_session_management
async def update_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    return await _update_noticelists(db, True)


# --- endpoint logic ---


async def _get_noticelist(db: Session, noticelist_id: int) -> NoticelistResponse:
    noticelist: Noticelist | None = await db.get(Noticelist, noticelist_id)

    if not noticelist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Noticelist not found.")

    result = await db.execute(select(NoticelistEntry).filter(NoticelistEntry.noticelist_id == noticelist_id))
    noticelist_entries = result.scalars().all()

    return NoticelistResponse(Noticelist=_prepare_noticelist_response(noticelist, noticelist_entries))


async def _toggleEnable_noticelists(db: Session, noticelist_id: int) -> StandardStatusIdentifiedResponse:
    noticelist: Noticelist | None = await db.get(Noticelist, noticelist_id)

    if not noticelist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Noticelist not found.")

    message = "disabled" if noticelist.enabled else "enabled"

    noticelist.enabled = not noticelist.enabled

    await db.commit()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name=f"Noticelist {message}.",
        message=f"Noticelist {message}.",
        url=f"/noticelists/toggleEnable/{noticelist_id}",
        id=noticelist_id,
    )


async def _update_noticelists(db: Session, depr: bool) -> StandardStatusResponse:
    return StandardStatusResponse(
        saved=True,
        success=True,
        name="All noticelists are up to date already.",
        message="All noticelists are up to date already.",
        url="/noticelists/update" if depr is True else "/noticelists/",
    )


async def _get_all_noticelists(db: Session) -> dict:
    noticelist_data: list[GetAllNoticelist] = []

    result = await db.execute(select(Noticelist))
    noticelists: list[Noticelist] = result.scalars().all()

    for noticelist in noticelists:
        noticelist_data.append(
            GetAllNoticelist(
                Noticelist=NoticelistAttributes(
                    id=noticelist.id,
                    name=noticelist.name,
                    expanded_name=noticelist.expanded_name,
                    ref=json.loads(noticelist.ref),
                    geographical_area=json.loads(noticelist.geographical_area),
                    version=noticelist.version,
                    enabled=noticelist.enabled,
                )
            )
        )

    return GetAllNoticelistResponse(response=noticelist_data)


def _prepare_noticelist_entries(noticelist_entries: list[NoticelistEntry]) -> list[NoticelistEntryResponse]:
    noticelist_entry_response = []
    for noticelist_entry in noticelist_entries:
        noticelist_entry_response_attribute = NoticelistEntryResponse(
            id=noticelist_entry.id, noticelist_id=noticelist_entry.noticelist_id, data=json.loads(noticelist_entry.data)
        )
        noticelist_entry_response.append(noticelist_entry_response_attribute)

    return noticelist_entry_response


def _prepare_noticelist_response(
    noticelist: Noticelist, noticelist_entries: list[NoticelistEntry]
) -> NoticelistAttributesResponse:
    return NoticelistAttributesResponse(
        id=noticelist.id,
        name=noticelist.name,
        expanded_name=noticelist.expanded_name,
        ref=json.loads(noticelist.ref),
        geographical_area=json.loads(noticelist.geographical_area),
        version=noticelist.version,
        enabled=noticelist.enabled,
        NoticelistEntry=_prepare_noticelist_entries(noticelist_entries),
    )
