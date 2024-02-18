from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.warninglists.check_value_warninglists_body import CheckValueWarninglistsBody
from mmisp.api_schemas.warninglists.check_value_warninglists_response import (
    CheckValueWarninglistsResponse,
    NameWarninglist,
    ValueWarninglistsResponse,
)
from mmisp.api_schemas.warninglists.create_warninglist_body import CreateWarninglistBody
from mmisp.api_schemas.warninglists.get_selected_all_warninglists_response import GetSelectedAllWarninglistsResponse
from mmisp.api_schemas.warninglists.get_selected_warninglists_body import GetSelectedWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_response import ToggleEnableWarninglistsResponse
from mmisp.api_schemas.warninglists.update_all_warninglists_response import UpdateAllWarninglistsResponse
from mmisp.api_schemas.warninglists.warninglist_response import WarninglistEntryResponse, WarninglistResponse
from mmisp.db.database import get_db
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry
from mmisp.util.request_validations import check_existence_and_raise

router = APIRouter(tags=["warninglists"])


@router.post(
    "/warninglists/new",
    status_code=status.HTTP_201_CREATED,
    response_model=WarninglistResponse,
    summary="Add a new warninglist",
    description="Add a new warninglist with given details.",
)
async def add_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WARNINGLIST]))],
    db: Annotated[Session, Depends(get_db)],
    body: CreateWarninglistBody,
) -> dict:
    return await _add_warninglist(db, body)


@router.get(
    "/warninglists/{warninglistId}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details",
    description="Retrieve details of a specific warninglist by its ID.",
)
async def view_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: str = Path(..., alias="warninglistId"),
) -> dict:
    return await _view_warninglist(db, warninglist_id)


@router.post(
    "/warninglists/toggleEnable",
    status_code=status.HTTP_200_OK,
    response_model=ToggleEnableWarninglistsResponse,
    summary="Disable/Enable warninglist",
    description="Disable/Enable a specific warninglist by its ID or name.",
)
async def post_toggleEnable(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    body: ToggleEnableWarninglistsBody,
) -> dict:
    return await _toggleEnable(db, body)


@router.delete(
    "/warninglists/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Delete warninglist",
    description="Delete a specific warninglist.",
)
async def delete_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: str = Path(..., alias="id"),
) -> dict:
    return await _delete_warninglist(db, warninglist_id)


@router.get(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=GetSelectedAllWarninglistsResponse,
    summary="Get all warninglists, or selected ones by value and status",
    description="Retrieve a list of all warninglists.",
)
async def get_all_or_selected_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[Session, Depends(get_db)],
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    return await _get_all_or_selected_warninglists(db, value, enabled)


@router.post(
    "/warninglists/checkValue",
    status_code=status.HTTP_200_OK,
    response_model=CheckValueWarninglistsResponse,
    summary="Get a list of ID and name of warninglists",
    description="Retrieve a list of ID and name of warninglists, which match has the given search term as Entry.",
)
async def get_warninglists_by_value(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[Session, Depends(get_db)],
    body: CheckValueWarninglistsBody,
) -> dict:
    return await _get_warninglists_by_value(db, body)


@router.put(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=UpdateAllWarninglistsResponse,
    summary="Update warninglists",
    description="Update all warninglists.",
)
async def update_all_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_all_warninglists(db, False)


@router.post(
    "/warninglists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=UpdateAllWarninglistsResponse,
    summary="Update warninglists (Deprecated)",
    description="Deprecated. Update all warninglists.",
)
async def update_all_warninglists_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SITE_ADMIN]))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _update_all_warninglists(db, True)


@router.get(
    "/warninglists/view/{warninglistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific warninglist by its ID using the old route.",
)
async def view_warninglist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[Session, Depends(get_db)],
    warninglist_id: str = Path(..., alias="warninglistId"),
) -> dict:
    return await _view_warninglist(db, warninglist_id)


@router.post(
    "/warninglists",
    deprecated=True,
    summary="Get selected warninglists (Deprecated)",
    description="Retrieve a list of warninglists, which match given search terms using the old route.",
)
async def search_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL))],
    db: Annotated[Session, Depends(get_db)],
    body: GetSelectedWarninglistsBody,
) -> dict:
    return await _get_selected_warninglists(db, body)


# --- endpoint logic ---


async def _add_warninglist(
    db: Session,
    body: CreateWarninglistBody,
) -> dict:
    warninglist_entry_count = len(body.values.splitlines())
    create = body.dict()
    create.pop("values")
    new_warninglist = Warninglist(
        **{
            **create,
            "warninglist_entry_count": warninglist_entry_count,
        }
    )

    db.add(new_warninglist)
    db.flush()
    db.refresh(new_warninglist)

    new_warninglist_entries = _create_warninglist_entries(body.values, new_warninglist.id)

    db.add_all(new_warninglist_entries)
    db.commit()

    warninglist_data = _prepare_warninglist_response(new_warninglist, new_warninglist_entries)

    return warninglist_data


async def _toggleEnable(
    db: Session,
    body: ToggleEnableWarninglistsBody,
) -> dict:
    warninglist_id_str_list = _convert_to_list(body.id)
    warninglist_id_list = [int(id_str) for id_str in warninglist_id_str_list]
    warninglist_name_list = _convert_to_list(body.name)

    warninglists: list[Warninglist] = (
        db.query(Warninglist)
        .filter(or_(Warninglist.id.in_(warninglist_id_list), Warninglist.name.in_(warninglist_name_list)))
        .all()
    )

    for warninglist in warninglists:
        warninglist.enabled = body.enabled

    db.commit()

    errors = ""
    success = ""
    if not len(warninglists):
        status = False
        errors = "Warninglist(s) not found"
    else:
        action = "enabled"

        if not body.enabled:
            action = "disabled"

        status = True
        success = f"{len(warninglists)} warninglist(s) {action}"

    return ToggleEnableWarninglistsResponse(saved=status, success=success, errors=errors)


async def _view_warninglist(
    db: Session,
    warninglist_id: str,
) -> dict:
    warninglist: Warninglist = check_existence_and_raise(
        db, Warninglist, warninglist_id, "id", "Warninglist not found."
    )

    warninglist_entries = _get_warninglist_entries(db, int(warninglist_id))

    warninglist_data = _prepare_warninglist_response(warninglist, warninglist_entries)

    return warninglist_data


async def _delete_warninglist(
    db: Session,
    warninglist_id: str,
) -> dict:
    warninglist: Warninglist = check_existence_and_raise(
        db, Warninglist, warninglist_id, "id", "Warninglist not found."
    )

    warninglist_entries = _get_warninglist_entries(db, int(warninglist_id))

    for warninglist_entry in warninglist_entries:
        db.delete(warninglist_entry)

    db.delete(warninglist)

    db.commit()

    return _prepare_warninglist_response(warninglist, warninglist_entries)


async def _get_all_or_selected_warninglists(
    db: Session,
    value: str = None,
    enabled: bool = None,
) -> dict:
    warninglists = _search_warninglist(db, value, enabled)

    warninglists_data = []
    for warninglist in warninglists:
        warninglist_entries = _get_warninglist_entries(db, warninglist.id)
        warninglists_data.append(_prepare_warninglist_response(warninglist, warninglist_entries))

    return GetSelectedAllWarninglistsResponse(response=warninglists_data)


async def _get_warninglists_by_value(
    db: Session,
    body: CheckValueWarninglistsBody,
) -> dict:
    values = body.value

    response: list[ValueWarninglistsResponse] = []

    for value in values:
        warninglist_entries: list[WarninglistEntry] = (
            db.query(WarninglistEntry).filter(WarninglistEntry.value == value).all()
        )

        warninglists: list[NameWarninglist] = []
        for warninglist_entry in warninglist_entries:
            warninglist: Warninglist = db.get(Warninglist, warninglist_entry.warninglist_id)
            if warninglist:
                warninglists.append(NameWarninglist(id=warninglist.id, name=warninglist.name))

        value_response = ValueWarninglistsResponse(
            value=value,
            NameWarninglist=warninglists,
        )

        response.append(value_response)

    return CheckValueWarninglistsResponse(response=response)


async def _update_all_warninglists(
    db: Session,
    deprecated: bool,
) -> dict:
    number_updated_lists = db.query(Warninglist).count()
    saved = True
    success = True
    name = "Succesfully updated " + str(number_updated_lists) + "warninglists."
    message = "Succesfully updated " + str(number_updated_lists) + "warninglists."
    url = "/warninglists/update" if deprecated else "/warninglists"

    return UpdateAllWarninglistsResponse(
        saved=saved,
        success=success,
        name=name,
        message=message,
        url=url,
    )


async def _get_selected_warninglists(
    db: Session,
    body: GetSelectedWarninglistsBody,
) -> dict:
    warninglists = _search_warninglist(db, body.value, body.enabled)

    warninglists_data = []

    for warninglist in warninglists:
        warninglist_entries = _get_warninglist_entries(db, int(warninglist.id))
        warninglists_data.append(_prepare_warninglist_response(warninglist, warninglist_entries))

    return GetSelectedAllWarninglistsResponse(response=warninglists_data)


def _search_warninglist(
    db: Session,
    value: str = None,
    enabled: bool = None,
) -> list[Warninglist]:
    query = db.query(Warninglist)

    if enabled is not None:
        query = query.filter(Warninglist.enabled.is_(enabled))
    if value is not None:
        query = query.filter(
            or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value)
        )

    warninglists: list[Warninglist] = query.all()

    return warninglists


def _create_warninglist_entries(
    values: str,
    warninglist_id: int,
) -> list[WarninglistEntry]:
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


def _convert_to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return [value]
    return value


def _prepare_warninglistEntry_response(warninglist_entry: WarninglistEntry) -> WarninglistEntryResponse:
    if not warninglist_entry:
        return None

    return WarninglistEntryResponse(
        id=str(warninglist_entry.id),
        value=warninglist_entry.value,
        warninglist_id=warninglist_entry.warninglist_id,
        comment=warninglist_entry.comment,
    )


def _prepare_warninglist_response(
    warninglist: Warninglist,
    warninglist_entries: list[WarninglistEntry] | None,
) -> WarninglistResponse:
    warninglist_entries_response = []

    if warninglist_entries:
        for warninglist_entry in warninglist_entries:
            warninglist_entries_response.append(_prepare_warninglistEntry_response(warninglist_entry))

    warninglist_data = WarninglistResponse(
        id=str(warninglist.id),
        name=warninglist.name,
        type=warninglist.type,
        description=warninglist.description,
        version=warninglist.version,
        enabled=warninglist.enabled,
        default=warninglist.default,
        category=warninglist.category,
        warninglist_entry_count=warninglist.warninglist_entry_count,
        WarninglistEntry=warninglist_entries_response,
    )

    return warninglist_data


def _get_warninglist_entries(
    db: Session,
    warninglist_id: int,
) -> list[WarninglistEntry]:
    warninglist_entries: list[WarninglistEntry] = (
        db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == str(warninglist_id)).all()
    )

    return warninglist_entries
