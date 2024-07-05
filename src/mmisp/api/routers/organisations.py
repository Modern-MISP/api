from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.organisations import GetOrganisationResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.util.partial import partial

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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
) -> GetOrganisationResponse:
    """
    Gets an organisation by its ID.

    Input:

    - ID of the organisation to get

    - The current database

    - new: The Users authentification status

    Output:

    - Data of the searched organisation
    """
    return await _get_organisation(auth, db, organisation_id)


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


async def _get_organisation(auth: Auth, db: Session, organisationID: str) -> GetOrganisationResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    query = select(Organisation).where(Organisation.id == organisationID)

    result = await db.execute(query)
    organisation = result.scalar_one_or_none()

    if organisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    return GetOrganisationResponse(
        id=organisation.id,
        name=organisation.name,
        date_created=organisation.date_created,
        date_modified=organisation.date_modified,
        description=organisation.description,
        type=organisation.type,
        nationality=organisation.nationality,
        sector=organisation.sector,
        created_by=organisation.created_by,
        uuid=organisation.uuid,
        contacts=organisation.contacts,
        local=organisation.local,
        restricted_to_domain=organisation.restricted_to_domain,
        landingpage=organisation.landingpage
    )


async def _delete_organisation(auth: Auth, db: Session, organisationID: str) -> None:
    return None


async def _update_organisation(auth: Auth, db: Session, organisationID: str) -> None:
    return None
