from typing import Annotated

from fastapi import APIRouter, Depends, Path

from mmisp.db.database import Session, get_db

router = APIRouter(tags=["statistics"])


@router.get(
    "/statistics/getUsageData",
    summary="Gets a list of all usage-related statistics listed on the website",
)
async def get_statistics(
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Gets all usage statistics as a list.

    Input:

    - db: Database session

    Output:

    - List of all usage statistics
    """
    return await _get_statistics(db)


@router.get(
    "/statistics/getAttributes/{orgId}",
    summary="Gets a list of attributes related to an organisation",
)
async def get_statistics_by_org(
    db: Annotated[Session, Depends(get_db)],
    org_id: Annotated[str, Path(alias="orgId")],
) -> None:
    """Gets all attrtibute-related statistics by organisation as a list.

    Input:

    - db: Database session
    - orgID: organisation ID

    Output:

    - List of all statistics related to an organisation
    """
    return await _get_statistics_by_org(db, org_id)


@router.get(
    "/statistics/logincount/{orgID}",
    summary="Gets a count of all logins the past 4 months",
)
async def get_logincount(
    db: Annotated[Session, Depends(get_db)],
    org_id: Annotated[str, Path(alias="orgID")],
) -> None:
    """Gets the login count of the past 4 months.

    Input:

    - db: Database session

    Output:

    - Count of all logins in the past 4 months
    """
    return await _get_logincount(db, org_id)


# --- endpoint logic ---


async def _get_statistics(db: Session) -> None:
    return None


async def _get_statistics_by_org(db: Session, orgID: str) -> None:
    return None


async def _get_logincount(db: Session, orgID: str) -> None:
    return None
