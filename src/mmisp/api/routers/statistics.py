from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from mmisp.db.database import Session, get_db

router = APIRouter(tags=["statistics"])

@router.get(
    "/statistics/getAttributes",
    summary="Gets a list of all attribute-related statistics listed on the website",
)
async def get_statistics(
    TODO
) : 
    """Gets all statistics as a list.
    
    Input:

    - db: Database session

    Output:

    - List of all statistics
    """
    return await _get_statistics(db)

@router.get(
    "/statistics/getAttributes/{orgId}",
    summary="Gets a list of attributes related to an organisation",
)
async def get_statistics(
    TODO
) : 
    """Gets all attrtibute-related statistics by organisation as a list.
    
    Input:

    - db: Database session
    - orgID: organisation ID

    Output:

    - List of all statistics related to an organisation
    """
    return await _get_statistics_by_org(db, orgID)

@router.get(
    "/statistics/logincount/{orgID}",
    summary="Gets a count of all logins the past 4 months",
)
async def get_logincount(
    TODO
) : 
    """Gets the login count of the past 4 months.
    
    Input:

    - db: Database session

    Output:
    
    - Count of all logins in the past 4 months
    """
    return await _get_logincount(db)

# --- endpoint logic ---

async def _get_statistics(db: Session) : return None

async def _get_statistics_by_org(db: Session, orgID: str) : return None

async def _get_logincount(db: Session, orgID: str) : return None

