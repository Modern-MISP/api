import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.users import (
    AddUserBody,
    AddUserResponse,
    GetAllUsersResponse,
    GetAllUsersUser,
    UsersViewMeResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.util.partial import partial

router = APIRouter(tags=["users"])


@router.post(
    "/users",
    summary="Add new user",
)
async def add_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddUserBody,
) -> AddUserResponse:
    """
    Adds a new user with the given details.

    Input:

    - Data representing the new user to be added

    - The current database

    Output:

    - Data representing the attributes of the new user
    """
    return await _add_user(auth=auth, db=db, body=body)


@router.get("/users/view/me.json", response_model=partial(UsersViewMeResponse))
@router.get("/users/view/me", response_model=partial(UsersViewMeResponse))
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Retrieves information about the logged in user.

    Input:

    - Authentication details of the logged in user

    Output:

    - Information about the logged in user
    """
    user = await db.get(User, auth.user_id)
    organisation = await db.get(Organisation, auth.org_id)
    role = await db.get(Role, auth.role_id)

    return {"User": user.__dict__, "Organisation": organisation.__dict__, "Role": role.__dict__}


@router.get(
    "/users/view/all",
    summary="Get all users",
)
async def get_all_users(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> GetAllUsersResponse:
    """
    Retrieves a list of all users.

    Input:

    - None

    Output:

    - List containing all users
    """
    return await _get_all_users(auth=auth, db=db)


@router.get(
    "/users/view/{userId}",
    summary="Get a user by id",
)
async def get_user_by_id(TODO):
    """
    Retrieves a user specified by id.

    Input:

    - ID of the user to get

    - The current database

    Output:

    - Data representing the attributes of the searched user
    """
    return await _get_user(db, userId)


@router.delete(
    "/users/{userId}",
    # response_model=UserAttributesResponse,
    summary="Delete a user",
)
async def delete_user(TODO):
    """
    Deletes a user by their ID.

    Input:

    - ID of the user to delete

    - The current database

    Output:

    - Response indicating success or failure
    """
    return await _delete_user(db, userID)


@router.delete(
    "/users/tokens/{userId}",
    # response_model=UserAttributesResponse,
    summary="Delete a users login token",
)
async def delete_user_token(TODO):
    """
    Deletes a users login token by their ID.

    Input:

    - ID of the user with the token to delete

    - The current database

    Output:

    - Response indicating success or failure
    """
    return await _delete_user_token(db, userID)


@router.put(
    "/users/{userId}",
    # response_model=UserAttributesResponse,
    summary="Update a user",
)
async def update_user(TODO):
    """
    Updates an existing user by their ID.

    Input:

    - ID of the user to update

    - Updated data for the user

    - The current database

    Output:

    - Data representing the updated attributes of the user
    """
    return await _update_user(db, userID)


# --- endpoint logic ---


async def _add_user(auth: Auth, db: Session, body: AddUserBody) -> AddUserResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = User(
        org_id=body.org_id,
        email=body.email,
        password=body.password,
        # autoalert: bool,
        invited_by=auth.user_id,
        gpgkey=body.gpgkey,
        # certif_public: str,
        termsaccepted=body.termsaccepted,
        role_id=body.role_id,
        change_pw=True,
        # contactalert: bool,
        disabled=body.disabled,
        # expiration: datetime,
        # current_login: str,
        last_login=int(time.time()),
        force_logout=False,
        date_created=int(time.time()),
        date_modified=int(time.time()),
        external_auth_required=False,
        # external_auth_key: str,
        # last_api_access: str,
        notification_daily=body.notification_daily,
        notification_weekly=body.notification_weekly,
        notification_monthly=body.notification_monthly,
        totp=body.totp,
        hotp_counter=None,
        last_pw_change=int(time.time()),
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)
    return AddUserResponse(id=user.id)


async def _get_all_users(
    auth: Auth,
    db: Session,
) -> GetAllUsersResponse:
    query = select(User)

    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    result = await db.execute(query)
    result = result.fetchall()
    user_list_computed: list[GetAllUsersUser] = []

    for user in result[0]:
        user_list_computed.append(
            GetAllUsersUser(
                id=user.id,
                organisation=user.org_id,
                role=user.role_id,
                nids=user.nids_sid,
                name="Test",
                email=user.email,
                last_login=user.last_login,
                created=user.date_created,
                totp=user.totp,
                contact=user.contactalert,
                notification=user.notification_daily or user.notification_weekly or user.notification_monthly,
                gpg_key=user.gpgkey,
                terms=user.termsaccepted,
            )
        )

    print(user_list_computed)

    return GetAllUsersResponse(users=user_list_computed)


async def _get_user(db: Session, userID: str):
    return None


async def _delete_user(db: Session, userID: str):
    return None


async def _delete_user_token(db: Session, userID: str):
    return None


async def _update_user(db: Session, userID: str):
    return None
