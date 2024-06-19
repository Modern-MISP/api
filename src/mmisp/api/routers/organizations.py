from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize
from mmisp.api_schemas.events import (
    AddEditGetEventGalaxyClusterRelation,
    AddEditGetEventGalaxyClusterRelationTag,
)

from mmisp.api_schemas.organisations import Organisation as OrganisationSchema
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation

router = APIRouter(tags=["organizations"])

@router.post(
    "/organisations",
    summary="Add a new organisation",
)
async def add_organisation(
    TODO
) : 
    """
    Adds a new organisation.

    Input:
    - Data representing the organisation to be added
    
    Output:
    - The added organisation data
    """
    return await _add_organisation(db, organisation)

@router.get(
    "/organisations/all",
    summary="Gets a list of all organisations",
)
async def get_organisations(
    TODO
) : 
    """
    Gets all organisations as a list.

    Input: None

    Output:
    - List of all organisations
    """
    return await _get_organisations(db)

@router.get(
    "/organisations/{orgId}",
    summary="Gets an organisation by its ID",
)
async def get_organisation(
    TODO
) : 
    """
    Gets an organisation by its ID.

    Input:
    - ID of the organisation to get
    
    Output:
    - Data of the searched organisation
    """
    return await _get_organisation(db, organisationID)

@router.delete(
    "/organisations/delete/{orgId}",
    summary="Deletes an organisation by its ID",
)
async def delete_organisation(
    TODO
) : 
    """
    Deletes an organisation by its ID.

    Input:
    - ID of the organisation to delete
    
    Output:
    - Response indicating success or failure
    """
    return await _delete_organisation(db, organisationID)

@router.post(
"/organisations/update/{orgId}",
summary="Updates an organisation by its ID",
)
async def update_organisation(
    TODO
) : 
    """
    Updates an organisation by its ID.

    Input:
    - ID of the organisation to update
    - Updated data for the organisation
    
    Output:
    - Updated organisation data
    """
    return await _update_organisation(db, organisationID)



# --- endpoint logic ---

async def _add_organisation(db: Session, organisation: Organisation) : return None

async def _get_organisations(db: Session) : return None

async def _get_organisation(db: Session, organisationID: str) : return None

async def _delete_organisation(db: Session, organisationID: str) : return None

async def _update_organisation(db: Session, organisationID: str) : return None

