import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.organisations import (
    AddOrganisation,
    DeleteForceUpdateOrganisationResponse,
    EditOrganisation,
    GetAllOrganisationResponse,
    GetAllOrganisationsOrganisation,
    GetOrganisationElement,
    GetOrganisationResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.lib.logger import alog

router = APIRouter(tags=["organisations"])


@router.post(
    "/organisations",
    summary="Add a new organisation",
)
@alog
async def add_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddOrganisation,
) -> GetOrganisationElement:
    """
    Adds a new organisation.

    args:

    - Data representing the organisation to be added

    - The current database

    returns:

    - The added organisation data
    """
    return await _add_organisation(auth, db, body)


@router.get(
    "/organisations/all",
    summary="Gets a list of all organisations",
)
@alog
async def get_organisations(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetAllOrganisationResponse]:
    """
    Gets all organisations as a list.

    args:

    - The current database

    returns:

    - List of all organisations
    """
    return await _get_organisations(auth, db)


@router.get(
    "/organisations",
    summary="Gets a list of all organisations",
    deprecated=True,
)
@router.get(
    "/organisations/index",
    summary="Gets a list of all organisations",
    deprecated=True,
)
@alog
async def get_organisations_deprecated(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetAllOrganisationResponse]:
    """
    Gets all organisations as a list.

    args:

    - The current database

    returns:

    - List of all organisations
    """
    return await _get_organisations(auth, db)


@router.get(
    "/organisations/{orgId}",
    summary="Gets an organisation by its ID",
)
@alog
async def get_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[int | uuid.UUID, Path(alias="orgId")],
) -> GetOrganisationElement:
    """
    Gets an organisation by its ID.

    args:

    - ID of the organisation to get

    - The current database

    - new: The Users authentification status

    returns:

    - Data of the searched organisation
    """
    return await _get_organisation(auth, db, organisation_id)


@router.get("/organisations/view/{orgId}", summary="Gets an organisation by its ID or UUID")
async def get_organisation_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[int | uuid.UUID, Path(alias="orgId")],
) -> GetOrganisationResponse:
    """
    Gets an organisation by its ID or UUID.

    Args:
      organisation_id: ID or UUID of the organisation to get
      db: The current database

    Returns:
      Data of the searched organisation
    """
    org = await _get_organisation(auth, db, organisation_id)
    return GetOrganisationResponse(Organisation=org)


@router.delete(
    "/organisations/delete/{orgId}",
    summary="Deletes an organisation by its ID",
)
@alog
async def delete_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
) -> DeleteForceUpdateOrganisationResponse:
    """
    Deletes an organisation by its ID.

    args:

    - ID of the organisation to delete

    - The current database

    returns:

    - Response indicating success or failure
    """
    return await _delete_organisation(auth, db, organisation_id)


@router.post(
    "/organisations/update/{orgId}",
    summary="Updates an organisation by its ID",
)
@alog
async def update_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    organisation_id: Annotated[str, Path(alias="orgId")],
    body: EditOrganisation,
) -> GetOrganisationElement:
    """
    Updates an organisation by its ID.

    args:

    - ID of the organisation to update

    - Updated data for the organisation

    - The current database

    returns:

    - Updated organisation data
    """
    return await _update_organisation(auth, db, organisation_id, body)


# --- deprecated ---

# --- endpoint logic ---


@alog
async def _add_organisation(auth: Auth, db: Session, body: AddOrganisation) -> GetOrganisationElement:
    if not (check_permissions(auth, [Permission.SITE_ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if body.uuid is None:
        body.uuid = uuid.uuid4()

    org = Organisation(
        name=body.name,
        date_created=datetime.now(),
        date_modified=datetime.now(),
        description=body.description,
        type=body.type,
        nationality=body.nationality,
        sector=body.sector,
        created_by=body.created_by,
        uuid=body.uuid,
        contacts=body.contacts,
        local=body.local,
        restricted_to_domain=body.restricted_to_domain,
        landingpage=body.landingpage,
    )
    db.add(org)
    await db.flush()
    return GetOrganisationElement(
        id=org.id,
        name=org.name,
        date_created=org.date_created,
        date_modified=org.date_modified,
        description=org.description,
        type=org.type,
        nationality=org.nationality,
        sector=org.sector,
        created_by=org.created_by,
        uuid=org.uuid,
        contacts=org.contacts,
        local=org.local,
        restricted_to_domain=org.restricted_to_domain,
        landingpage=org.landingpage,
    )


@alog
async def _get_organisations(auth: Auth, db: Session) -> list[GetAllOrganisationResponse]:
    query = select(Organisation)
    result = await db.execute(query)
    organisations = result.scalars().all()
    org_list_computed: list[GetAllOrganisationResponse] = []

    for organisation in organisations:
        org_list_computed.append(
            GetAllOrganisationResponse(
                Organisation=GetAllOrganisationsOrganisation(
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
                    landingpage=organisation.landingpage,
                    user_count=organisation.user_count,
                    created_by_email=organisation.creator.email if organisation.creator is not None else "",
                )
            )
        )

    return org_list_computed


@alog
async def _get_organisation(auth: Auth, db: Session, organisation_id: int | uuid.UUID) -> GetOrganisationElement:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) or check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(Organisation)
    if isinstance(organisation_id, int):
        query = query.where(Organisation.id == organisation_id)
    else:
        query = query.where(Organisation.uuid == organisation_id)

    result = await db.execute(query)
    organisation = result.scalar_one_or_none()

    if organisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    return GetOrganisationElement(
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
        landingpage=organisation.landingpage,
    )


@alog
async def _delete_organisation(auth: Auth, db: Session, organisationID: str) -> DeleteForceUpdateOrganisationResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    organisation = await db.get(Organisation, organisationID)

    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateOrganisationResponse(
                saved=False,
                success=False,
                name="Invalid organisation.",
                message="Invalid organisation.",
                url=f"/organisations/{organisationID}",
            ).dict(),
        )

    await db.delete(organisation)
    await db.flush()

    return DeleteForceUpdateOrganisationResponse(
        saved=True,
        success=True,
        name="Organisation deleted",
        message="Organisation deleted",
        url=f"/organisations/{organisationID}",
    )


@alog
async def _update_organisation(
    auth: Auth, db: Session, organisationID: str, body: EditOrganisation
) -> GetOrganisationElement:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    org = await db.get(Organisation, organisationID)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DeleteForceUpdateOrganisationResponse(
                saved=False,
                success=False,
                name="Invalid organisation.",
                message="Invalid organisation.",
                url=f"/organisations/{organisationID}",
            ).dict(),
        )
    org.name = body.name
    if body.description is not None:
        org.description = body.description
    org.type = body.type
    if body.nationality is not None:
        org.nationality = body.nationality
    if body.sector is not None:
        org.sector = body.sector
    if body.contacts is not None:
        org.contacts = body.contacts
    org.local = body.local
    if body.restricted_to_domain is not None:
        org.restricted_to_domain = body.restricted_to_domain
    if body.landingpage is not None:
        org.landingpage = body.landingpage

    await db.flush()
    await db.refresh(org)
    return GetOrganisationElement(
        id=org.id,
        name=org.name,
        date_created=org.date_created,
        date_modified=org.date_modified,
        description=org.description,
        type=org.type,
        nationality=org.nationality,
        sector=org.sector,
        created_by=org.created_by,
        uuid=org.uuid,
        contacts=org.contacts,
        local=org.local,
        restricted_to_domain=org.restricted_to_domain,
        landingpage=org.landingpage,
    )
