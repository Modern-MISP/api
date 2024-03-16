from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import delete, func, or_
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.standard_status_response import StandardStatusResponse
from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody
from mmisp.api_schemas.warninglists.check_value_warninglists_response import (
    CheckValueWarninglistsResponse,
    NameWarninglist,
    ValueWarninglistsResponse,
)
from mmisp.api_schemas.warninglists.create_warninglist_body import CreateWarninglistBody
from mmisp.api_schemas.warninglists.get_selected_all_warninglists_response import (
    GetSelectedAllWarninglistsResponse,
    WarninglistsResponse,
)
from mmisp.api_schemas.warninglists.get_selected_warninglists_body import GetSelectedWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_response import ToggleEnableWarninglistsResponse
from mmisp.api_schemas.warninglists.warninglist_response import (
    WarninglistResponse,
)
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry, WarninglistType
from mmisp.util.partial import partial

router = APIRouter(tags=["warninglists"])


@router.post(
    "/warninglists/new",
    status_code=status.HTTP_201_CREATED,
    response_model=WarninglistResponse,
    summary="Add a new warninglist",
    description="Add a new warninglist with given details.",
)
@with_session_management
async def add_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.WARNINGLIST]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateWarninglistBody,
) -> WarninglistResponse:
    return await _add_warninglist(db, body)


@router.get(
    "/warninglists/{warninglistId}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details",
    description="Retrieve details of a specific warninglist by its ID.",
)
@with_session_management
async def get_warninglist_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="warninglistId")],
) -> WarninglistResponse:
    return await _get_warninglist_details(db, warninglist_id)


@router.post(
    "/warninglists/toggleEnable",
    status_code=status.HTTP_200_OK,
    response_model=ToggleEnableWarninglistsResponse,
    response_model_exclude_unset=True,
    summary="Disable/Enable warninglist",
    description="Disable/Enable a specific warninglist by its ID or name.",
)
@with_session_management
async def post_toggleEnable(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: ToggleEnableWarninglistsBody,
) -> ToggleEnableWarninglistsResponse:
    return await _toggleEnable(db, body)


@router.delete(
    "/warninglists/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Delete warninglist",
    description="Delete a specific warninglist.",
)
@with_session_management
async def delete_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="id")],
) -> WarninglistResponse:
    return await _delete_warninglist(db, warninglist_id)


@router.get(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=partial(GetSelectedAllWarninglistsResponse),
    summary="Get all warninglists, or selected ones by value and status",
    description="Receive a list of all warning lists, or when setting the path parameters value and enabled, receive a \
        list of warninglists for which the value matches either the name, description, or type and enabled matches \
        given parameter.",
)
@with_session_management
async def get_all_or_selected_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    return await _get_all_or_selected_warninglists(db, value, enabled)


@router.post(
    "/warninglists/checkValue",
    status_code=status.HTTP_200_OK,
    response_model=partial(CheckValueWarninglistsResponse),
    summary="Get a list of ID and name of enabled warninglists",
    description="Retrieve a list of ID and name of enabled warninglists, \
        which match has the given search term as entry.",
)
@with_session_management
async def get_warninglists_by_value(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: CheckValueWarninglistsBody,
) -> dict:
    return await _get_warninglists_by_value(db, body)


@router.put(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update warninglists",
    description="Update all warninglists.",
)
@with_session_management
async def update_all_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    return await _update_all_warninglists(db, False)


# --- deprecated ---


@router.get(
    "/warninglists/view/{warninglistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific warninglist by its ID using the old route.",
)
@with_session_management
async def get_warninglist_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="warninglistId")],
) -> WarninglistResponse:
    return await _get_warninglist_details(db, warninglist_id)


@router.post(
    "/warninglists",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=partial(GetSelectedAllWarninglistsResponse),
    summary="Get selected warninglists (Deprecated)",
    description="Retrieve a list of warninglists, which match given search terms using the old route.",
)
@with_session_management
async def search_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: GetSelectedWarninglistsBody,
) -> dict:
    return await _get_selected_warninglists(db, body)


@router.post(
    "/warninglists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=StandardStatusResponse,
    summary="Update warninglists (Deprecated)",
    description="Deprecated. Update all warninglists.",
)
@with_session_management
async def update_all_warninglists_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    return await _update_all_warninglists(db, True)


# --- endpoint logic ---


async def _add_warninglist(
    db: Session,
    body: CreateWarninglistBody,
) -> dict:
    create = body.dict()
    create.pop("values")
    create.pop("valid_attributes")

    new_warninglist = Warninglist(**{**create})

    db.add(new_warninglist)

    await db.flush()
    await db.refresh(new_warninglist)

    new_warninglist_entries = _create_warninglist_entries(body.values, new_warninglist.id)
    new_warninglist_types = _create_warninglist_types(body.valid_attributes, new_warninglist.id)

    db.add_all(new_warninglist_entries)
    db.add_all(new_warninglist_types)

    await db.commit()

    warninglist_data = await _prepare_warninglist_details_response(db, new_warninglist)

    return WarninglistResponse(warninglist=warninglist_data)


async def _toggleEnable(
    db: Session,
    body: ToggleEnableWarninglistsBody,
) -> dict:
    warninglist_id_str_list = _convert_to_list(body.id)
    warninglist_id_list = [int(id_str) for id_str in warninglist_id_str_list]
    warninglist_name_list = _convert_to_list(body.name)

    result = await db.execute(
        select(Warninglist).filter(
            or_(Warninglist.id.in_(warninglist_id_list), Warninglist.name.in_(warninglist_name_list))
        )
    )
    warninglists: list[Warninglist] = result.scalars().all()

    for warninglist in warninglists:
        warninglist.enabled = body.enabled

    await db.commit()

    if not warninglists:
        return ToggleEnableWarninglistsResponse(saved=False, errors="Warninglist(s) not found")

    action = "enabled"
    if not body.enabled:
        action = "disabled"

    return ToggleEnableWarninglistsResponse(saved=True, success=f"{len(warninglists)} warninglist(s) {action}")


async def _get_warninglist_details(
    db: Session,
    warninglist_id: int,
) -> dict:
    warninglist: Warninglist | None = await db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_response = await _prepare_warninglist_details_response(db, warninglist)

    return WarninglistResponse(warninglist=warninglist_response)


async def _delete_warninglist(
    db: Session,
    warninglist_id: int,
) -> dict:
    warninglist: Warninglist | None = await db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_entry_count = await _get_warninglist_entry_count(db, warninglist_id)

    result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id))
    warninglist_entries = result.scalars().all()

    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types = result.scalars().all()

    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = warninglist_entry_count
    warninglist_response["valid_attributes"] = valid_attributes
    warninglist_response["warninglist_entry"] = [
        warninglist_entry.__dict__ for warninglist_entry in warninglist_entries
    ]
    warninglist_response["warninglist_type"] = [warninglist_type.__dict__ for warninglist_type in warninglist_types]

    await db.execute(delete(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist.id))
    await db.execute(delete(WarninglistType).filter(WarninglistType.warninglist_id == warninglist.id))
    await db.delete(warninglist)
    await db.commit()

    return WarninglistResponse(warninglist=warninglist_response)


async def _get_all_or_selected_warninglists(
    db: Session,
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    warninglists: list[Warninglist] = await _search_warninglist(db, value, enabled)

    warninglists_data: list[WarninglistsResponse] = []
    for warninglist in warninglists:
        warninglists_data.append(WarninglistsResponse(warninglist=await _prepare_warninglist_response(db, warninglist)))

    return GetSelectedAllWarninglistsResponse(warninglists=warninglists_data)


async def _get_warninglists_by_value(
    db: Session,
    body: CheckValueWarninglistsBody,
) -> dict:
    values = body.value

    response: list[ValueWarninglistsResponse] = []

    for value in values:
        result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.value == value))
        warninglist_entries: list[WarninglistEntry] = result.scalars().all()

        name_warninglists: list[NameWarninglist] = []
        for warninglist_entry in warninglist_entries:
            result = await db.execute(
                select(Warninglist).filter(
                    Warninglist.id == warninglist_entry.warninglist_id, Warninglist.enabled.is_(True)
                )
            )
            warninglists: Warninglist = result.scalars().all()
            for warninglist in warninglists:
                name_warninglists.append(NameWarninglist(id=warninglist_entry.warninglist_id, name=warninglist.name))

        value_response = ValueWarninglistsResponse(
            value=value,
            warninglist=name_warninglists,
        )

        response.append(value_response)

    return CheckValueWarninglistsResponse(response=response)


async def _update_all_warninglists(
    db: Session,
    deprecated: bool,
) -> StandardStatusResponse:
    name = "All warninglists are up to date already."
    message = "All warninglists are up to date already."
    url = "/warninglists/update" if deprecated else "/warninglists"

    return StandardStatusResponse(
        saved=True,
        success=True,
        name=name,
        message=message,
        url=url,
    )


async def _get_selected_warninglists(
    db: Session,
    body: GetSelectedWarninglistsBody,
) -> dict:
    warninglists: list[Warninglist] = await _search_warninglist(db, body.value, body.enabled)

    warninglists_data: list[WarninglistsResponse] = []
    for warninglist in warninglists:
        warninglists_data.append(WarninglistsResponse(warninglist=await _prepare_warninglist_response(db, warninglist)))

    return GetSelectedAllWarninglistsResponse(warninglists=warninglists_data)


async def _search_warninglist(db: Session, value: str | None = None, enabled: bool | None = None) -> list[Warninglist]:
    query = select(Warninglist)

    if enabled is not None:
        query = query.filter(Warninglist.enabled.is_(enabled))
    if value is not None:
        query = query.filter(
            or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value)
        )

    result = await db.execute(query.order_by(Warninglist.id.desc()))
    warninglists: list[Warninglist] = result.scalars().all()

    return warninglists


def _create_warninglist_entries(values: str, warninglist_id: int) -> list[WarninglistEntry]:
    raw_text = values.splitlines()
    new_warninglist_entries = []

    for line in raw_text:
        comment: str = ""

        line_split = line.split("#", 1)

        if len(line_split) > 1:
            comment = line_split.pop()

        value = line_split.pop()

        new_warninglist_entry = WarninglistEntry(
            value=value,
            comment=comment,
            warninglist_id=str(warninglist_id),
        )

        new_warninglist_entries.append(new_warninglist_entry)

    return new_warninglist_entries


def _create_warninglist_types(valid_attributes: list[str], warninglist_id: int) -> list[WarninglistType]:
    new_warninglist_types: list[WarninglistType] = []
    for valid_attribute in valid_attributes:
        new_warninglist_type = WarninglistType(type=valid_attribute, warninglist_id=warninglist_id)
        new_warninglist_types.append(new_warninglist_type)

    return new_warninglist_types


def _convert_to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return [value]
    return value


async def _prepare_warninglist_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = await _get_warninglist_entry_count(db, warninglist.id)
    warninglist_response["valid_attributes"] = await _get_valid_attributes(db, warninglist.id)

    return warninglist_response


async def _prepare_warninglist_details_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = await _prepare_warninglist_response(db, warninglist)
    warninglist_response["warninglist_entry"] = await _get_warninglist_entries(db, warninglist.id)
    warninglist_response["warninglist_type"] = await _get_warninglist_types(db, warninglist.id)

    return warninglist_response


async def _get_warninglist_types(db: Session, warninglist_id: int) -> list[dict]:
    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types = result.scalars().all()
    return [warninglist_type.__dict__ for warninglist_type in warninglist_types]


async def _get_warninglist_entries(db: Session, warninglist_id: int) -> list[dict]:
    result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id))
    warninglist_entries = result.scalars().all()
    return [warninglist_entry.__dict__ for warninglist_entry in warninglist_entries]


async def _get_warninglist_entry_count(db: Session, warninglist_id: int) -> int:
    result = await db.execute(select(func.count()).filter(WarninglistEntry.warninglist_id == warninglist_id))
    return result.scalar()


async def _get_valid_attributes(db: Session, warninglist_id: int) -> str:
    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types: list[WarninglistType] = result.scalars().all()

    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    return valid_attributes
