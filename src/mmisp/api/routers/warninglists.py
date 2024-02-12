import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
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
logging.basicConfig(level=logging.INFO)

info_format = "%(asctime)s - %(message)s"
error_format = "%(asctime)s - %(filename)s:%(lineno)d - %(message)s"

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(info_format))

error_handler = logging.StreamHandler()
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(error_format))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(info_handler)
logger.addHandler(error_handler)

# TODO:  db: Session = Depends(get_db), or db: Annotated[Session, Depends(get_db)],


@router.post(
    "/warninglists/new",
    status_code=status.HTTP_201_CREATED,
    response_model=WarninglistResponse,
    summary="Add a new warninglist",
    description="Add a new warninglist with given details.",
)
async def add_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: CreateWarninglistBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _add_warninglist(body, db)


@router.get(
    "/warninglists/{warninglistId}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details",
    description="Retrieve details of a specific warninglist by its ID.",
)
async def view_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    body: ToggleEnableWarninglistsBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _toggleEnable(body, db)


@router.delete(
    "/warninglists/{id}",
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Delete warninglist",
    description="Delete a specific warninglist.",
)
async def delete_warninglist(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY, Permission.WARNINGLIST]))],
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
async def get_all_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD, Permission.WARNINGLIST]))],
    db: Annotated[Session, Depends(get_db)],
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    return await _get_all_warninglists(db)  # , value, enabled)


# @router.get(
#     "/warninglists?value=String&enabled=boolean",
#     summary="Get selected warninglists",
#     description="Retrieve a list of warninglists, which match given search terms using the old route.",
# )
# async def get_warninglists_by_param(value: str, enabled: bool) -> GetSelectedAllWarninglistsResponse:
#     return None


@router.post(
    "/warninglists/checkValue",
    status_code=status.HTTP_200_OK,
    response_model=CheckValueWarninglistsResponse,
    summary="Get a list of ID and name of warninglists",
    description="Retrieve a list of ID and name of warninglists, which match has the given search term as Entry.",
)
async def get_warninglists_by_value(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.FULL]))],
    body: CheckValueWarninglistsBody,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return await _get_warninglists_by_value(body, db)


@router.put(
    "/warninglists",
    status_code=status.HTTP_200_OK,
    response_model=UpdateAllWarninglistsResponse,
    summary="Update warninglists",
    description="Update all warninglists.",
)
async def update_all_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.ADD]))],
    db: Session = Depends(get_db),
) -> dict:
    return await _update_all_warninglists(db)


# DEPRECATED ENDPOINTS
@router.post(
    "/warninglists/update",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=UpdateAllWarninglistsResponse,
    summary="Update warninglists (Deprecated)",
    description="Deprecated. Update all warninglists.",
)
async def update_all_warninglists_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.SYNC]))],
    db: Session = Depends(get_db),
) -> dict:
    return await _update_all_warninglists(db)


@router.get(
    "/warninglists/view/{warninglistId}",
    deprecated=True,
    status_code=status.HTTP_200_OK,
    response_model=WarninglistResponse,
    summary="Get warninglist details (Deprecated)",
    description="Deprecated. Retrieve details of a specific warninglist by its ID using the old route.",
)
async def view_warninglist_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.MODIFY]))],
    db: Session = Depends(get_db),
    warninglist_id: str = Path(..., alias="warninglistId"),
) -> dict:
    return await _view_warninglist(db, warninglist_id)


@router.post(
    "/warninglists/",
    deprecated=True,
    summary="Get selected warninglists (Deprecated)",
    description="Retrieve a list of warninglists, which match given search terms using the old route.",
)
async def search_warninglists(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.ALL, [Permission.WARNINGLIST]))],
    body: GetSelectedWarninglistsBody,
    db: Session = Depends(get_db),
) -> dict:
    return await _get_selected_warninglists(body, db)


# --- endpoint logic ---
async def _add_warninglist(
    body: CreateWarninglistBody,
    db: Session,
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

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to add new warninglist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    for new_warninglist_entry in new_warninglist_entries:
        db.refresh(new_warninglist_entry)

    logger.info(f"New warninglist added: {new_warninglist.id}")

    warninglist_data = _prepare_warninglist_response(new_warninglist, new_warninglist_entries)

    return warninglist_data


async def _toggleEnable(
    body: ToggleEnableWarninglistsBody,
    db: Session,
) -> dict:
    warninglist_id_list = _convert_to_list(body.id)
    for id in warninglist_id_list:
        id = int(id)
    warninglist_name_list = _convert_to_list(body.name)
    warninglist_enabled = body.enabled
    # Imlementation like old/current route. Maybe optimize later. Only looks after warninglist_ids
    # if not warninglist_id_list:
    #     for warninglist_name in warninglist_name_list:
    #         warninglists = db.query(Warninglist).filter(Warninglist.id == warninglist_name).all()
    #         for warninglist in warninglists:
    #             warninglist.enabled = warninglist_enabled  # type: ignore
    #             counter += 1
    #             db.commit()

    for warninglist_id in warninglist_id_list:
        warninglist = db.query(Warninglist).filter(Warninglist.id == warninglist_id).first()
        if warninglist:
            warninglist.enabled = warninglist_enabled  # type: ignore
        db.commit()

    id_filter = db.query(Warninglist).filter(Warninglist.id.in_(warninglist_id_list))
    name_filter = db.query(Warninglist).filter(Warninglist.name.in_(warninglist_name_list))

    updated_warninglists = id_filter.union(name_filter).all()

    # updated_warninglists = db.query(Warninglist).filter(Warninglist.id == 228).all()

    disable_status = "disabled" if body.enabled is False else "enabled"
    if not updated_warninglists:
        status = False
        message = "Warninglist(s) not found"
    else:
        for updated_warninglist in updated_warninglists:
            updated_warninglist.enabled = body.enabled
        number_updated_warninglists = len(updated_warninglists)
        status = True
        message = str(number_updated_warninglists) + " warninglist(s) " + disable_status

    try:
        db.commit()
        logger.info(f"Warninglists '{disable_status}'.")
    except SQLAlchemyError:
        db.rollback()
        logger.exception(f"Failed to '{disable_status}'d warninglists.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return ToggleEnableWarninglistsResponse(saved=status, success=message)


async def _view_warninglist(
    db: Session,
    warninglist_id: str,
) -> dict:
    warninglist: Warninglist = check_existence_and_raise(
        db, Warninglist, warninglist_id, "id", "Warninglist not found."
    )
    # TODO: best practice? already known warninglist_id is a int
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

    # TODO: best practice? already known warninglist_id is a int
    warninglist_entries = _get_warninglist_entries(db, int(warninglist_id))

    for warninglist_entry in warninglist_entries:
        db.delete(warninglist_entry)

    db.delete(warninglist)

    try:
        db.commit()
        logger.info(f"Deleted warninglist with id '{warninglist_id}'.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Failed to delete warninglist with id '{warninglist_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred."
        )

    return _prepare_warninglist_response(warninglist, warninglist_entries)


async def _get_all_warninglists(
    db: Session,
    value: str | None = None,
    enabled: bool | None = None,
) -> dict:
    # TODO: optimize
    if value is not None and enabled is not None:
        warninglists = (
            db.query(Warninglist)
            .filter(
                (
                    and_(
                        or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value),
                        Warninglist.enabled == enabled,
                    )
                )
            )
            .all()
        )
    elif value is not None:
        warninglists = (
            db.query(Warninglist)
            .filter(or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value))
            .all()
        )
    elif enabled is not None:
        warninglists = db.query(Warninglist).filter(Warninglist.enabled == enabled).all()
    else:
        warninglists = db.query(Warninglist).all()

    warninglists_data = []
    for warninglist in warninglists:
        warninglist_entries = _get_warninglist_entries(db, int(warninglist.id))
        warninglists_data.append(_prepare_warninglist_response(warninglist, warninglist_entries))

    return GetSelectedAllWarninglistsResponse(response=warninglists_data)


async def _get_warninglists_by_value(
    body: CheckValueWarninglistsBody,
    db: Session,
) -> dict:
    values = body.value

    response: list[ValueWarninglistsResponse] = []

    for value in values:
        warninglist_entries = db.query(WarninglistEntry).filter(WarninglistEntry.value == value).all()

        warninglists: list[NameWarninglist] = []
        for warninglist_entry in warninglist_entries:
            warninglist = db.query(Warninglist).filter(Warninglist.id == int(warninglist_entry.warninglist_id)).first()
            warninglists.append(NameWarninglist(id=warninglist.id, name=warninglist.name))

        value_response = ValueWarninglistsResponse(
            value=value,
            NameWarninglist=warninglists,
        )

        response.append(value_response)

    return CheckValueWarninglistsResponse(response=response)


async def _update_all_warninglists(
    db: Session,
) -> dict:
    number_updated_lists = db.query(Warninglist).count()
    saved = True
    success = True
    name = "Succesfully updated " + str(number_updated_lists) + "warninglists."
    message = "Succesfully updated " + str(number_updated_lists) + "warninglists."
    url = "/warninglists/"

    return UpdateAllWarninglistsResponse(
        saved=saved,
        success=success,
        name=name,
        message=message,
        url=url,
    )


async def _get_selected_warninglists(
    body: GetSelectedWarninglistsBody,
    db: Session,
) -> dict:
    # TODO: optimize
    value = body.value
    enabled = body.enabled
    if value is not None and enabled is not None:
        warninglists = (
            db.query(Warninglist)
            .filter(
                (
                    and_(
                        or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value),
                        Warninglist.enabled == enabled,
                    )
                )
            )
            .all()
        )
    elif value is not None:
        warninglists = (
            db.query(Warninglist)
            .filter(or_(Warninglist.name == value, Warninglist.description == value, Warninglist.type == value))
            .all()
        )
    elif enabled is not None:
        warninglists = db.query(Warninglist).filter(Warninglist.enabled == enabled).all()
    else:
        warninglists = []

    warninglists_data = []
    for warninglist in warninglists:
        warninglist_entries = _get_warninglist_entries(db, int(warninglist.id))
        warninglists_data.append(_prepare_warninglist_response(warninglist, warninglist_entries))

    return GetSelectedAllWarninglistsResponse(response=warninglists_data)


def _create_warninglist_entries(values: str, warninglist_id: int) -> list[WarninglistEntry]:
    raw_text = values.splitlines()
    new_warninglist_entries = []
    for line in raw_text:
        comment: str
        if len(line.split("#", 1)) > 1:
            comment = line.split("#", 1)[1]
        else:
            comment = ""
        value = line.split("#", 1)[0]
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
    if warninglist_entry is not None:
        return WarninglistEntryResponse(
            id=str(warninglist_entry.id),
            value=warninglist_entry.value,
            warninglist_id=warninglist_entry.warninglist_id,
            comment=warninglist_entry.comment,
        )
    return None


def _prepare_warninglist_response(
    warninglist: Warninglist, warninglist_entries: list[WarninglistEntry] | None
) -> WarninglistResponse:
    warninglist_entries_response = []
    if warninglist_entries is not None:
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


def _get_warninglist_entries(db: Session, warninglist_id: int) -> list[WarninglistEntry]:
    warninglist_entries: list[WarninglistEntry] | None = (
        db.query(WarninglistEntry).filter(WarninglistEntry.warninglist_id == str(warninglist_id)).all()
    )
    if warninglist_entries is None:
        warninglist_entries = []

    return warninglist_entries
