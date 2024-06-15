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
    """adds a new organisation"""
    return await _add_organisation(db, organisation)

@router.get(
    "/organisations/all",
    summary="gets a list of all organisations",
)
async def get_organisations(
    TODO
) : 
    """gets all organisation as a list"""
    return await _get_organisations(db)

@router.get(
    "/organisations/{orgId}",
    summary="gets an organisation by its ID",
)
async def get_organisation(
    TODO
) : 
    """gets an organisation by its ID"""
    return await _get_organisation(db, organisationID)

@router.delete(
    "/organisations/delete/{orgId}",
    summary="deletes an organisation by its ID",
)
async def delete_organisation(
    TODO
) : 
    """deletes an organisation by its ID"""
    return await _delete_organisation(db, organisationID)

@router.post(
"/organisations/update/{orgId}",
summary="updates an organisation by its ID",
)
async def update_organisation(
    TODO
) : 
    """updates an organisation by its ID"""
    return await _update_organisation(db, organisationID)



# --- endpoint logic ---

async def _add_organisation(db: Session, organisation: Organisation) : return None

async def _get_organisations(db: Session) : return None

async def _get_organisation(db: Session, organisationID: str) : return None

async def _delete_organisation(db: Session, organisationID: str) : return None

async def _update_organisation(db: Session, organisationID: str) : return None

