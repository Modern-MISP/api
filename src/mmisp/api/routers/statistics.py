from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, authorize
from mmisp.api_schemas.statistics import OrgDataResponseModel, UsageDataResponseModel
from mmisp.db.database import Session, get_db
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.user import User
from mmisp.lib.logger import alog

router = APIRouter(tags=["statistics"])


@router.get(
    "/statistics/getUsageData",
    summary="Gets a list of all usage-related statistics listed on the website",
)
@alog
async def get_statistics(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> UsageDataResponseModel:
    """Gets all usage statistics as a list.

    args:

    - db: Database session

    returns:

    - List of all usage statistics
    """
    return await _get_statistics(db)


@router.get(
    "/statistics/getAttributes/{orgId}",
    summary="Gets a list of attributes related to an organisation",
)
@alog
async def get_statistics_by_org(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    org_id: Annotated[str, Path(alias="orgId")],
) -> OrgDataResponseModel:
    """Gets all attrtibute-related statistics by organisation as a list.

    args:

    - db: Database session
    - orgID: organisation ID

    returns:

    - List of all statistics related to an organisation
    """
    return await _get_statistics_by_org(db, org_id)


@router.get(
    "/statistics/logincount/{orgID}",
    summary="Gets a count of all logins the past 4 months",
)
@alog
async def get_logincount(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    org_id: Annotated[str, Path(alias="orgID")],
) -> int:
    """Gets the login count of the past 4 months.

    args:

    - db: Database session

    returns:

    - Count of all logins in the past 4 months
    """
    return await _get_logincount(db, org_id)


# --- endpoint logic ---


@alog
async def _get_statistics(db: Session) -> UsageDataResponseModel:
    query = select(Event)
    events_result = await db.execute(query)
    events_list = events_result.fetchall()
    event_count = len(events_list)

    query = select(Organisation)
    org_result = await db.execute(query)
    org_list = org_result.fetchall()
    org_count = len(org_list)

    query = select(User)
    user_result = await db.execute(query)
    users_list = user_result.fetchall()
    user_count = len(users_list)

    query = select(Attribute)
    attribute_result = await db.execute(query)
    attribute_list = attribute_result.fetchall()
    attribute_count = len(attribute_list)

    user_with_gpgkey_count = 0
    for user in users_list:
        if len(user[0].gpgkey.strip()) > 0:
            user_with_gpgkey_count = user_with_gpgkey_count + 1

    eventAttribute_count = 0
    for event in events_list:
        eventAttribute_count = eventAttribute_count + event[0].attribute_count

    localOrg_count = 0
    for org in org_list:
        if org[0].local:
            localOrg_count = localOrg_count + 1

    all_events = []
    if len(events_list) > 0:
        eventCreatorOrg_count = 1
        all_events.append(events_list[0])

    for event in events_list:
        current_event = event[0]

        for event2 in all_events:
            if event2[0].orgc_id != current_event.orgc_id:
                all_events.append(current_event)
                eventCreatorOrg_count = eventCreatorOrg_count + 1
                break

    users_per_org = []

    for org in org_list:
        counter = 0
        for user in users_list:
            if org[0].id == user[0].org_id:
                counter = counter + 1
        users_per_org.append(counter)

    averageUsers = sum(users_per_org) / len(users_per_org)

    response = UsageDataResponseModel(
        events=event_count,
        attributes=attribute_count,
        eventAttributes=eventAttribute_count,
        users=user_count,
        usersWithGPGKeys=user_with_gpgkey_count,
        organisations=org_count,
        localOrganisations=localOrg_count,
        eventCreatorOrgs=eventCreatorOrg_count,
        averageUsersPerOrg=averageUsers,
    )
    return response


@alog
async def _get_statistics_by_org(db: Session, orgID: str) -> OrgDataResponseModel:
    int_orgId = 0
    try:
        int_orgId = int(orgID)

    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    query = select(User)
    user_result = await db.execute(query)
    users_list = user_result.fetchall()

    query = select(Event)
    events_result = await db.execute(query)
    events_list = events_result.fetchall()

    user_count = 0
    for user in users_list:
        if user[0].org_id == int_orgId:
            user_count = user_count + 1
    event_count = 0
    attribute_count = 0

    for event in events_list:
        if event[0].org_id == int_orgId:
            event_count = event_count + 1
            attribute_count = attribute_count + event[0].attribute_count

    response = OrgDataResponseModel(
        users=user_count,
        events=event_count,
        attributes=attribute_count,
    )
    return response


@alog
async def _get_logincount(db: Session, orgID: str) -> int:
    int_orgId = 0
    try:
        int_orgId = int(orgID)

    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    query = select(User)
    user_result = await db.execute(query)
    users_list = user_result.fetchall()
    login_count = 0
    for user in users_list:
        if user[0].org_id == int_orgId:
            login_count = login_count + user[0].newsread
    return login_count
