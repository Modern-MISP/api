from fastapi import APIRouter

from mmisp.db.database import Session

router = APIRouter(tags=["statistics"])


@router.get(
    "/statistics/getUsageData",
    summary="Gets a list of all usage-related statistics listed on the website",
)
async def get_statistics(TODO):
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
async def get_statistics_by_org(TODO):
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
async def get_logincount(TODO):
    """Gets the login count of the past 4 months.

    Input:

    - db: Database session

    Output:

    - Count of all logins in the past 4 months
    """
    return await _get_logincount(db)


# --- endpoint logic ---


async def _get_statistics(db: Session) -> None:
    return None


async def _get_statistics_by_org(db: Session, orgID: str) -> None:
    return None


async def _get_logincount(db: Session, orgID: str) -> None:
    return None
