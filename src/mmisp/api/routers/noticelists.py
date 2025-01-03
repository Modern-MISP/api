import json
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.noticelists import (
    GetAllNoticelists,
    NoticelistAttributes,
    NoticelistAttributesResponse,
    NoticelistEntryResponse,
    NoticelistResponse,
)
from mmisp.api_schemas.responses.standard_status_response import (
    StandardStatusIdentifiedResponse,
    StandardStatusResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.noticelist import Noticelist, NoticelistEntry
from mmisp.lib.logger import alog, log

router = APIRouter(tags=["noticelists"])


@router.get(
    "/noticelists/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=NoticelistResponse,
    summary="Get noticelist details",
)
@alog
async def get_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> NoticelistResponse:
    """Retrieve details of a specific noticelist by its ID.

    args:

    - the user's authentification status

    - the current database

    - the notice list id

    returns:

    - the details of the notice list
    """
    return await _get_noticelist(db, noticelist_id)


@router.post(
    "/noticelists/toggleEnable/{noticelistId}",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusIdentifiedResponse,
)
@alog
async def post_toggleEnable_noticelist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> StandardStatusIdentifiedResponse:
    """Disable/Enable a specific noticelist by its ID.

    args:

    - the user's authentification status

    - the current database

    - the notice list id

    returns:

    - the enabled/disabled notice list
    """
    return await _toggleEnable_noticelists(db, noticelist_id)


@router.put(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update noticelists",
)
@alog
async def update_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """Update all noticelists.

    args:

    - the user's authentification status

    - the current database

    returns:

    - all updated notice lists
    """
    return await _update_noticelists(db, False)


@router.get(
    "/noticelists",
    status_code=status.HTTP_200_OK,
    response_model=list[GetAllNoticelists],
    summary="Get all noticelists",
)
@alog
async def get_all_noticelists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetAllNoticelists]:
    """Retrieve a list of all noticelists.

    args:

    - the user's authentification status

    - the current database

    returns:

    - all notice lists as a list
    """
    return await _get_all_noticelists(db)


# --- deprecated ---


@router.get(
    "/noticelists/view/{noticelistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=NoticelistResponse,
    summary="Get noticelist details (Deprecated)",
)
@alog
async def get_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    noticelist_id: Annotated[int, Path(alias="noticelistId")],
) -> NoticelistResponse:
    """Deprecated. Retrieve details of a specific noticelist by its ID using the old route.

    args:

    - the user's authentification status

    - the current database

    - the id of the notice list

    returns:

    - the details of the notice list
    """
    return await _get_noticelist(db, noticelist_id)


@router.post(
    "/noticelists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update noticelists (Deprecated)",
)
@alog
async def update_noticelist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """Deprecated. Update all noticelists.

    args:

    - the user's authentification status

    - the current database

    returns:

    - all updated notice lists
    """
    return await _update_noticelists(db, True)


# --- endpoint logic ---


@alog
async def _get_noticelist(db: Session, noticelist_id: int) -> NoticelistResponse:
    noticelist: Noticelist | None = await db.get(Noticelist, noticelist_id)

    if not noticelist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Noticelist not found.")

    result = await db.execute(select(NoticelistEntry).filter(NoticelistEntry.noticelist_id == noticelist_id))
    noticelist_entries = result.scalars().all()

    return NoticelistResponse(Noticelist=_prepare_noticelist_response(noticelist, noticelist_entries))


@alog
async def _toggleEnable_noticelists(db: Session, noticelist_id: int) -> StandardStatusIdentifiedResponse:
    noticelist: Noticelist | None = await db.get(Noticelist, noticelist_id)

    if not noticelist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Noticelist not found.")

    message = "disabled" if noticelist.enabled else "enabled"

    noticelist.enabled = not noticelist.enabled

    await db.flush()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name=f"Noticelist {message}.",
        message=f"Noticelist {message}.",
        url=f"/noticelists/toggleEnable/{noticelist_id}",
        id=noticelist_id,
    )


@alog
async def _update_noticelists(db: Session, depr: bool) -> StandardStatusResponse:
    return StandardStatusResponse(
        saved=True,
        success=True,
        name="All noticelists are up to date already.",
        message="All noticelists are up to date already.",
        url="/noticelists/update" if depr else "/noticelists/",
    )


@alog
async def _get_all_noticelists(db: Session) -> list[GetAllNoticelists]:
    noticelist_data: list[GetAllNoticelists] = []

    result = await db.execute(select(Noticelist))
    noticelists: Sequence[Noticelist] = result.scalars().all()

    for noticelist in noticelists:
        noticelist_data.append(
            GetAllNoticelists(
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

    return noticelist_data


@log
def _prepare_noticelist_entries(noticelist_entries: Sequence[NoticelistEntry]) -> list[NoticelistEntryResponse]:
    noticelist_entry_response = []
    for noticelist_entry in noticelist_entries:
        noticelist_entry_response_attribute = NoticelistEntryResponse(
            id=noticelist_entry.id, noticelist_id=noticelist_entry.noticelist_id, data=json.loads(noticelist_entry.data)
        )
        noticelist_entry_response.append(noticelist_entry_response_attribute)

    return noticelist_entry_response


@log
def _prepare_noticelist_response(
    noticelist: Noticelist, noticelist_entries: Sequence[NoticelistEntry]
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
