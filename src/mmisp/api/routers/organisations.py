import uuid
from datetime import datetime
from typing import Annotated

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.organisations import (
    AddOrganisation,
    DeleteForceUpdateOrganisationResponse,
    EditOrganisation,
    GetAllOrganisationResponse,
    GetAllOrganisationsOrganisation,
    GetOrganisationResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.user import User

router = APIRouter(tags=["organisations"])


@router.post(
    "/organisations",
    summary="Add a new organisation",
)
async def add_organisation(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddOrganisation,
) -> GetOrganisationResponse:
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
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetAllOrganisationResponse]:
    """
    Gets all organisations as a list.

    Input:

    - The current database

    Output:

    - List of all organisations
    """
    return await _get_organisations(auth, db)


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
) -> DeleteForceUpdateOrganisationResponse:
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
    body: EditOrganisation,
) -> GetOrganisationResponse:
    """
    Updates an organisation by its ID.

    Input:

    - ID of the organisation to update

    - Updated data for the organisation

    - The current database

    Output:

    - Updated organisation data
    """
    return await _update_organisation(auth, db, organisation_id, body)


# --- deprecated ---


@router.get(
    "/organisations",
    summary="Gets a list of all organisations",
    deprecated=True,
)
async def get_organisations_deprecated(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetAllOrganisationResponse]:
    """
    Gets all organisations as a list.

    Input:

    - The current database

    Output:

    - List of all organisations
    """
    return await _get_organisations(auth, db)


# --- endpoint logic ---


async def _add_organisation(auth: Auth, db: Session, body: AddOrganisation) -> GetOrganisationResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    org = Organisation(
        id=body.id,
        name=body.name,
        date_created=datetime.now(),
        date_modified=datetime.now(),
        description=body.description,
        type=body.type,
        nationality=body.nationality,
        sector=body.sector,
        created_by=body.created_by,
        uuid=uuid.uuid4().hex,
        contacts=body.contacts,
        local=body.local,
        restricted_to_domain=body.restricted_to_domain,
        landingpage=body.landingpage,
    )
    db.add(org)
    await db.commit()
    return GetOrganisationResponse(
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


async def _get_organisations(auth: Auth, db: Session) -> list[GetAllOrganisationResponse]:
    query = select(Organisation)
    result = await db.execute(query)
    organisations = result.fetchall()
    org_list_computed: list[GetAllOrganisationResponse] = []

    for organisation in organisations[0]:
        query_created_by = select(User).where(User.id == Organisation.created_by)
        result_created_by = await db.execute(query_created_by)
        created_by = result_created_by.scalar_one_or_none()

        query_user_count = select(sqlalchemy.func.count(User.id)).where(User.org_id == organisation.id)
        result_user_count = await db.execute(query_user_count)
        user_count = result_user_count.scalar_one_or_none()

        org_list_computed.append(
            GetAllOrganisationResponse(
                Organisation=GetAllOrganisationsOrganisation(
                    id=str(organisation.id),
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
                    user_count=user_count,
                    created_by_email=created_by.email if created_by else "Unknown",
                )
            )
        )

    return org_list_computed


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
        landingpage=organisation.landingpage,
    )


async def _delete_organisation(auth: Auth, db: Session, organisationID: str) -> DeleteForceUpdateOrganisationResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
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
    await db.commit()

    return DeleteForceUpdateOrganisationResponse(
        saved=True,
        success=True,
        name="Organisation deleted",
        message="Organisation deleted",
        url=f"/organisations/{organisationID}",
    )


async def _update_organisation(
    auth: Auth, db: Session, organisationID: str, body: EditOrganisation
) -> GetOrganisationResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
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

    await db.commit()
    await db.refresh(org)
    return GetOrganisationResponse(
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
