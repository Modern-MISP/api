from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import or_
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
from mmisp.api_schemas.warninglists.get_selected_all_warninglists_response import GetSelectedAllWarninglistsResponse
from mmisp.api_schemas.warninglists.get_selected_warninglists_body import GetSelectedWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.api_schemas.warninglists.toggle_enable_warninglists_response import ToggleEnableWarninglistsResponse
from mmisp.api_schemas.warninglists.warninglist_response import (
    WarninglistResponse,
)
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry, WarninglistType

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
) -> dict:
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
) -> dict:
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
) -> dict:
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
) -> dict:
    return await _delete_warninglist(db, warninglist_id)


@router.get(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=GetSelectedAllWarninglistsResponse,
    summary="Get all warninglists, or selected ones by value and status",
    description="Retrieve a list of all warninglists.",
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
    response_model=CheckValueWarninglistsResponse,
    summary="Get a list of ID and name of warninglists",
    description="Retrieve a list of ID and name of warninglists, which match has the given search term as Entry.",
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
) -> dict:
    return await _get_warninglist_details(db, warninglist_id)


@router.post(
    "/warninglists",
    deprecated=True,
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
    db.flush()
    db.refresh(new_warninglist)

    new_warninglist_entries = _create_warninglist_entries(body.values, new_warninglist.id)
    new_warninglist_types = _create_warninglist_types(body.valid_attributes, new_warninglist.id)

    db.add_all(new_warninglist_entries)
    db.add_all(new_warninglist_types)
    db.commit()

    warninglist_data = _prepare_warninglist_details_response(db, new_warninglist)

    return WarninglistResponse(Warninglist=warninglist_data)


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
    warninglist: Warninglist | None = db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_response = _prepare_warninglist_details_response(db, warninglist)

    return WarninglistResponse(Warninglist=warninglist_response)


async def _delete_warninglist(
    db: Session,
    warninglist_id: int,
) -> dict:
    warninglist: Warninglist | None = db.get(Warninglist, warninglist_id)

    if not warninglist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warninglist not found.")

    warninglist_entry_count = (
        db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id).count()
    )
    warninglist_entries = db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id).all()
    warninglist_types = db.query(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id).all()

    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = warninglist_entry_count
    warninglist_response["valid_attributes"] = valid_attributes
    warninglist_response["WarninglistEntry"] = [warninglist_entry.__dict__ for warninglist_entry in warninglist_entries]
    warninglist_response["WarninglistType"] = [warninglist_type.__dict__ for warninglist_type in warninglist_types]

    # for warninglist_entry in warninglist_entries:
    #     db.delete(warninglist_entry)

    # for warninglist_type in warninglist_types:
    #     db.delete(warninglist_type)

    db.delete(warninglist)

    db.commit()

    return WarninglistResponse(Warninglist=warninglist_response)


async def _get_all_or_selected_warninglists(
    db: Session,
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    warninglists = _search_warninglist(db, value, enabled)

    warninglists_data = []
    for warninglist in warninglists:
        warninglists_data.append(_prepare_warninglist_response(db, warninglist))

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
) -> StandardStatusResponse:
    number_updated_lists = db.query(Warninglist).count()
    saved = True
    success = True
    name = "Successfully updated " + str(number_updated_lists) + " warninglists."
    message = "Successfully updated " + str(number_updated_lists) + " warninglists."
    url = "/warninglists/update" if deprecated else "/warninglists"

    return StandardStatusResponse(
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
        warninglists_data.append(_prepare_warninglist_response(db, warninglist))

    return GetSelectedAllWarninglistsResponse(response=warninglists_data)


def _search_warninglist(
    db: Session,
    value: str | None = None,
    enabled: bool | None = None,
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


def _prepare_warninglist_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = warninglist.__dict__
    warninglist_response["warninglist_entry_count"] = _get_warninglist_entry_count(db, warninglist.id)
    warninglist_response["valid_attributes"] = _get_valid_attributes(db, warninglist.id)

    return warninglist_response


def _prepare_warninglist_details_response(db: Session, warninglist: Warninglist) -> dict:
    warninglist_response = _prepare_warninglist_response(db, warninglist)
    warninglist_response["WarninglistEntry"] = _get_warninglist_entries(db, warninglist.id)
    warninglist_response["WarninglistType"] = _get_warninglist_types(db, warninglist.id)

    return warninglist_response


def _get_warninglist_types(db: Session, warninglist_id: int) -> list[dict]:
    warninglist_types = db.query(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id).all()
    return [warninglist_type.__dict__ for warninglist_type in warninglist_types]


def _get_warninglist_entries(db: Session, warninglist_id: int) -> list[dict]:
    warninglist_entries = db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id).all()
    return [warninglist_entry.__dict__ for warninglist_entry in warninglist_entries]


def _get_warninglist_entry_count(db: Session, warninglist_id: int) -> int:
    return db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == warninglist_id).count()


def _get_valid_attributes(db: Session, warninglist_id: int) -> str:
    warninglist_types: list[WarninglistType] = (
        db.query(WarninglistType).filter(WarninglistType.warninglist_id == warninglist_id).all()
    )
    attributes = [warninglist_type.type for warninglist_type in warninglist_types]
    valid_attributes: str = ", ".join(attributes)

    return valid_attributes
