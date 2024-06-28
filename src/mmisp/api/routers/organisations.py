from typing import Annotated

from fastapi import APIRouter, Depends, Path

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.db.database import Session, get_db

router = APIRouter(tags=["organisations"])


@router.post(
    "/organisations",
    summary="Add a new organisation",
)
async def add_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: None,
) -> None:
    """
    Adds a new organisation.

    Input:

    - Data representing the organisation to be added

    - The current database

    Output:

    - The added organisation data
    """
    return await _add_organisation(auth, db, body)


@router.get(
    "/organisations/all",
    summary="Gets a list of all organisations",
)
async def get_organisations(
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Gets all organisations as a list.

    Input:

    - The current database

    Output:

    - List of all organisations
    """
    return await _get_organisations(db)


@router.get(
    "/organisations/{orgId}",
    summary="Gets an organisation by its ID",
)
async def get_organisation(
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
) -> None:
    """
    Gets an organisation by its ID.

    Input:

    - ID of the organisation to get

    - The current database

    Output:

    - Data of the searched organisation
    """
    return await _get_organisation(db, organisation_id)


@router.delete(
    "/organisations/delete/{orgId}",
    summary="Deletes an organisation by its ID",
)
async def delete_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
) -> None:
    """
    Deletes an organisation by its ID.

    Input:

    - ID of the organisation to delete

    - The current database

    Output:

    - Response indicating success or failure
    """
    return await _delete_organisation(auth, db, organisation_id)


@router.post(
    "/organisations/update/{orgId}",
    summary="Updates an organisation by its ID",
)
async def update_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
) -> None:
    """
    Updates an organisation by its ID.

    Input:

    - ID of the organisation to update

    - Updated data for the organisation

    - The current database

    Output:

    - Updated organisation data
    """
    return await _update_organisation(auth, db, organisation_id)


# --- endpoint logic ---


async def _add_organisation(auth: Auth, db: Session, body: None) -> None:
    return None


async def _get_organisations(db: Session) -> None:
    return None


async def _get_organisation(db: Session, organisationID: str) -> None:
    return None


async def _delete_organisation(auth: Auth, db: Session, organisationID: str) -> None:
    return None


async def _update_organisation(auth: Auth, db: Session, organisationID: str) -> None:
    return None
