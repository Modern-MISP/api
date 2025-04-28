from collections.abc import Sequence
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import delete, func, or_
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.responses.standard_status_response import StandardStatusResponse
from mmisp.api_schemas.warninglists import (
    CheckValueResponse,
    CheckValueWarninglistsBody,
    CreateWarninglistBody,
    GetSelectedAllWarninglistsResponse,
    GetSelectedWarninglistsBody,
    NameWarninglist,
    ToggleEnableWarninglistsBody,
    ToggleEnableWarninglistsResponse,
    WarninglistResponse,
    WarninglistsResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry, WarninglistType
from mmisp.lib.logger import alog, log

router = APIRouter(tags=["warninglists"])


@router.post(
    "/warninglists/new",
    status_code=status.HTTP_201_CREATED,
    summary="Add a new warninglist",
)
@alog
async def add_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WARNINGLIST]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateWarninglistBody,
) -> WarninglistResponse:
    """
    Add a new warninglist with given details.

    args:

    - auth: Authentication details

    - db: Database session

    - body: CreateWarninglistBody, Data for creating the new warninglist

    returns:

    - WarninglistResponse: Response with details of the new warninglist
    """
    return await _add_warninglist(db, body)


@router.get(
    "/warninglists/{warninglistId}",
    status_code=status.HTTP_200_OK,
    summary="Get warninglist details",
)
@alog
async def get_warninglist_details(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="warninglistId")],
) -> WarninglistResponse:
    """
    Retrieve details of a specific warninglist by its ID.

    args:

    - auth: Authentication details

    - db: Database session

    - warninglist_id: ID of the warninglist to fetch

    returns:

    - WarninglistResponse: Response with details of the searched warninglist
    """
    return await _get_warninglist_details(db, warninglist_id)


@router.post(
    "/warninglists/toggleEnable",
    status_code=status.HTTP_200_OK,
    response_model_exclude_unset=True,
    summary="Disable/Enable warninglist",
)
@alog
async def post_toggleEnable(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: ToggleEnableWarninglistsBody,
) -> ToggleEnableWarninglistsResponse:
    """
    Disable/Enable a specific warninglist by its ID or name.

    args:

    - auth: Authentication details

    - db:Database session

    - body: ToggleEnableWarninglistsBody, Data to toggle enable status of the warninglist

    returns:

    - ToggleEnableWarninglistsResponse: Response showing success or failure
    """
    return await _toggleEnable(db, body)


@router.delete(
    "/warninglists/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete warninglist",
)
@alog
async def delete_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="id")],
) -> WarninglistResponse:
    """
    Delete a specific warninglist.

    args:

    - auth: Authentication details

    - db: Database session

    - warninglist_id: ID of the warninglist to delete

    returns:

    - WarninglistResponse: Response showing success or failure
    """
    return await _delete_warninglist(db, warninglist_id)


@router.get(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    summary="Get all warninglists, or selected ones by value and status",
)
@alog
async def get_all_or_selected_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    value: str | None = None,
    enabled: bool | None = None,
) -> GetSelectedAllWarninglistsResponse:
    """
    Receive a list of all warning lists, or when setting the path parameters value and enabled, receive a \
        list of warninglists for which the value matches either the name, description, or type and enabled matches \
        given parameter.

    args:

    - auth: Authentication details

    - db: Database session

    - value: str | None, Search term for filtering by value

    - enabled: bool | None, Status filter (enabled or disabled)

    returns:

    - GetSelectedAllWarninglistsResponse: Response containing filtered or all warninglists
    """
    return await _get_all_or_selected_warninglists(db, value, enabled)


@router.post(
    "/warninglists/checkValue",
    status_code=status.HTTP_200_OK,
    summary="Get a list of ID and name of enabled warninglists",
)
@alog
async def get_warninglists_by_value(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: CheckValueWarninglistsBody,
) -> CheckValueResponse | dict:
    """
    Retrieve a list of ID and name of enabled warninglists, \
        which match has the given search term as entry.

    args:

    - auth: Authentication details

    - db: Database session

    - body: CheckValueWarninglistsBody, Data for searching warninglists by value

    returns:

    - CheckValueResponse | dict: Response with searched warninglists
    """
    return await _get_warninglists_by_value(db, body)


@router.put(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    summary="Update warninglists",
)
@alog
async def update_all_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """
    Update all warninglists.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusResponse: Response indicating success or failure
    """
    return await _update_all_warninglists(db, False)


# --- deprecated ---


@router.get(
    "/warninglists/view/{warninglistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Get warninglist details (Deprecated)",
)
@alog
async def get_warninglist_details_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: Annotated[int, Path(alias="warninglistId")],
) -> WarninglistResponse:
    """
    Deprecated. Retrieve details of a specific warninglist by its ID using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - warninglist_id: ID of the warninglist to fetch

    returns:

    - WarninglistResponse: Response with details of the searched warninglist
    """
    return await _get_warninglist_details(db, warninglist_id)


@router.post(
    "/warninglists",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Get selected warninglists (Deprecated)",
)
@alog
async def search_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: GetSelectedWarninglistsBody,
) -> GetSelectedAllWarninglistsResponse:
    """
    Retrieve a list of warninglists, which match given search terms using the old route.

    args:

    - auth: Authentication details

    - db: Database session

    - body: GetSelectedWarninglistsBody, Data for filtering warninglists

    returns:

    - GetSelectedAllWarninglistsResponse: Response containing filtered warninglists
    """
    return await _get_selected_warninglists(db, body)


@router.post(
    "/warninglists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    summary="Update warninglists (Deprecated)",
)
@alog
async def update_all_warninglists_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusResponse:
    """
    Deprecated. Update all warninglists.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusResponse: Response indicating success or failure
    """
    return await _update_all_warninglists(db, True)


# --- endpoint logic ---


@alog
async def _add_warninglist(
    db: Session,
    body: CreateWarninglistBody,
) -> WarninglistResponse:
    create = body.model_dump()
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

    await db.flush()

    warninglist_data = await _prepare_warninglist_details_response(db, new_warninglist)

    return WarninglistResponse(Warninglist=warninglist_data)


@alog
async def _toggleEnable(
    db: Session,
    body: ToggleEnableWarninglistsBody,
) -> ToggleEnableWarninglistsResponse:
    warninglist_id_str_list = _convert_to_list(body.id)
    warninglist_id_list: list[int] = []
    for id_str in warninglist_id_str_list:
        try:
            warninglist_id_list.append(int(id_str))
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Warninglist id musst be an integer.")
    warninglist_name_list = _convert_to_list(body.name)

    result = await db.execute(
        select(Warninglist).filter(
            or_(Warninglist.id.in_(warninglist_id_list), Warninglist.name.in_(warninglist_name_list))
        )
    )
    warninglists: Sequence[Warninglist] = result.scalars().all()

    for warninglist in warninglists:
        warninglist.enabled = body.enabled

    await db.flush()

    if not warninglists:
        return ToggleEnableWarninglistsResponse(saved=False, errors="Warninglist(s) not found")

    action = "enabled"
    if not body.enabled:
        action = "disabled"

    return ToggleEnableWarninglistsResponse(saved=True, success=f"{len(warninglists)} warninglist(s) {action}")


@alog
async def _get_warninglist_details(
    db: Session,
    warninglist_id: int,
) -> WarninglistResponse:
    warninglist: Warninglist | None = await db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_response = await _prepare_warninglist_details_response(db, warninglist)

    return WarninglistResponse(Warninglist=warninglist_response)


@alog
async def _delete_warninglist(
    db: Session,
    warninglist_id: int,
) -> WarninglistResponse:
    warninglist: Warninglist | None = await db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_entry_count = await _get_warninglist_entry_count(db, warninglist_id)

    result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id))
    warninglist_entries = result.scalars().all()

    del result
    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types = result.scalars().all()

    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = warninglist_entry_count
    warninglist_response["valid_attributes"] = valid_attributes
    warninglist_response["WarninglistEntry"] = [warninglist_entry.__dict__ for warninglist_entry in warninglist_entries]
    warninglist_response["WarninglistType"] = [warninglist_type.__dict__ for warninglist_type in warninglist_types]

    await db.execute(delete(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist.id))
    await db.execute(delete(WarninglistType).filter(WarninglistType.warninglist_id == warninglist.id))
    await db.delete(warninglist)
    await db.flush()

    return WarninglistResponse(Warninglist=warninglist_response)


@alog
async def _get_all_or_selected_warninglists(
    db: Session,
    value: str | None = None,
    enabled: bool | None = None,
) -> GetSelectedAllWarninglistsResponse:
    warninglists: Sequence[Warninglist] = await _search_warninglist(db, value, enabled)

    warninglists_data: list[WarninglistsResponse] = []
    for warninglist in warninglists:
        warninglists_data.append(WarninglistsResponse(Warninglist=await _prepare_warninglist_response(db, warninglist)))

    return GetSelectedAllWarninglistsResponse(Warninglists=warninglists_data)


@alog
async def _get_warninglists_by_value(
    db: Session,
    body: CheckValueWarninglistsBody,
) -> dict:
    value = body.value

    result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.value == value))
    warninglist_entries: Sequence[WarninglistEntry] = result.scalars().all()
    del result

    name_warninglists: list[NameWarninglist] = []
    for warninglist_entry in warninglist_entries:
        result = await db.execute(
            select(Warninglist).filter(
                Warninglist.id == warninglist_entry.warninglist_id, Warninglist.enabled.is_(True)
            )
        )
        warninglists: Sequence[Warninglist] = result.scalars().all()
        for warninglist in warninglists:
            name_warninglists.append(
                NameWarninglist(id=warninglist_entry.warninglist_id, name=warninglist.name, matched=value)
            )

    return {f"{value}": name_warninglists}


@alog
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


@alog
async def _get_selected_warninglists(
    db: Session,
    body: GetSelectedWarninglistsBody,
) -> GetSelectedAllWarninglistsResponse:
    warninglists: Sequence[Warninglist] = await _search_warninglist(db, body.value, body.enabled)

    warninglists_data: list[WarninglistsResponse] = []
    for warninglist in warninglists:
        warninglists_data.append(WarninglistsResponse(Warninglist=await _prepare_warninglist_response(db, warninglist)))

    return GetSelectedAllWarninglistsResponse(Warninglists=warninglists_data)


@alog
async def _search_warninglist(
    db: Session, value: str | None = None, enabled: bool | None = None
) -> Sequence[Warninglist]:
    query = select(Warninglist)

    if enabled is not None:
        query = query.filter(Warninglist.enabled.is_(enabled))
    if value is not None:
        query = query.filter(
            or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value)
        )

    result = await db.execute(query.order_by(Warninglist.id.desc()))
    warninglists: Sequence[Warninglist] = result.scalars().all()

    return warninglists


@log
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


@log
def _create_warninglist_types(valid_attributes: Sequence[str], warninglist_id: int) -> list[WarninglistType]:
    new_warninglist_types: list[WarninglistType] = []
    for valid_attribute in valid_attributes:
        new_warninglist_type = WarninglistType(type=valid_attribute, warninglist_id=warninglist_id)
        new_warninglist_types.append(new_warninglist_type)

    return new_warninglist_types


@log
def _convert_to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return [value]
    return value


@alog
async def _prepare_warninglist_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = await _get_warninglist_entry_count(db, warninglist.id)
    warninglist_response["valid_attributes"] = await _get_valid_attributes(db, warninglist.id)

    return warninglist_response


@alog
async def _prepare_warninglist_details_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = await _prepare_warninglist_response(db, warninglist)
    warninglist_response["WarninglistEntry"] = await _get_warninglist_entries(db, warninglist.id)
    warninglist_response["WarninglistType"] = await _get_warninglist_types(db, warninglist.id)

    return warninglist_response


@alog
async def _get_warninglist_types(db: Session, warninglist_id: int) -> list[dict]:
    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types = result.scalars().all()
    return [warninglist_type.__dict__ for warninglist_type in warninglist_types]


@alog
async def _get_warninglist_entries(db: Session, warninglist_id: int) -> list[dict]:
    result = await db.execute(select(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id))
    warninglist_entries = result.scalars().all()
    return [warninglist_entry.__dict__ for warninglist_entry in warninglist_entries]


@alog
async def _get_warninglist_entry_count(db: Session, warninglist_id: int) -> int:
    result = await db.execute(select(func.count()).filter(WarninglistEntry.warninglist_id == warninglist_id))
    return cast(int, result.scalar())


@alog
async def _get_valid_attributes(db: Session, warninglist_id: int) -> str:
    result = await db.execute(select(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id))
    warninglist_types: Sequence[WarninglistType] = result.scalars().all()

    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    return valid_attributes
