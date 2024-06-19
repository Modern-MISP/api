from collections.abc import Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.future import select
from starlette import status
from starlette.requests import Request

from mmisp.db.database import Session, get_db

router = APIRouter(tags=["statistics"])

@router.get(
    "/statistics/all",
    summary="Gets a list of all statistics listed on the website",
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
    "/statistics/logincount",
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

async def _get_logincount(db: Session) : return None

