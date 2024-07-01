import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.users import (
    AddUserBody,
    AddUserResponse,
    GetAllUsersUser,
    UserAttributesBody,
    UsersViewMeResponse,
    UserWithName,
)
from mmisp.api_schemas.users import (
    User as UserSchema,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.db.models.user_setting import UserSetting
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
) -> list[GetAllUsersUser]:
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
async def get_user_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
) -> GetAllUsersUser:
    """
    Retrieves a user specified by id.

    Input:

    - ID of the user to get

    - The current database

    Output:

    - Data representing the attributes of the searched user
    """
    return await _get_user(auth, db, user_id)


@router.delete(
    "/users/{user_id}",
    # response_model=UserAttributesResponse,
    summary="Delete a user",
)
async def delete_user(
    user_id: Annotated[int, Path(alias="userId")],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes a user by their ID.

    Input:

    - ID of the user to delete

    - auth: Authentication details of the current user

    - The current database

    Output:
    - StandardStatusIdentifiedResponse: Response indicating success or failure
    """
    await _delete_user(user_id=user_id, auth=auth, db=db)
    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="User deleted.",
        message="User deleted.",
        url=f"/users/{user_id}",
        id=user_id,
    )


@router.delete(
    "/users/tokens/{userId}",
    # response_model=UserAttributesResponse,
    summary="Delete a users login token",
)
async def delete_user_token(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
) -> None:
    """
    Deletes a users login token by their ID.

    Input:

    - ID of the user with the token to delete

    - The current database

    Output:

    - Response indicating success or failure
    """
    return await _delete_user_token(auth, db, user_id)


@router.put(
    "/users/{userId}",
    # response_model=UserAttributesResponse,
    summary="Update a user",
)
async def update_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
    body: UserAttributesBody,
) -> UserWithName:
    """
    Updates an existing user by their ID.

    Input:

    - ID of the user to update

    - Updated data for the user

    - The current database

    Output:

    - Data representing the updated attributes of the user
    """
    return await _update_user(auth, db, user_id, body)


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
        invited_by=auth.user_id,
        gpgkey=body.gpgkey,
        termsaccepted=body.termsaccepted,
        role_id=body.role_id,
        change_pw=True,
        disabled=body.disabled,
        force_logout=False,
        external_auth_required=False,
        notification_daily=body.notification_daily,
        notification_weekly=body.notification_weekly,
        notification_monthly=body.notification_monthly,
        totp=body.totp,
        hotp_counter=None,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    user_setting = UserSetting(
        user_id=user.id,
        setting="user_name",
        value=json.dumps({"name": str(body.name)}),
    )

    db.add(user_setting)

    await db.commit()
    await db.refresh(user_setting)

    return AddUserResponse(id=user.id)


async def _get_all_users(
    auth: Auth,
    db: Session,
) -> list[GetAllUsersUser]:
    query = select(User)

    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    result = await db.execute(query)
    users = result.fetchall()
    user_list_computed: list[GetAllUsersUser] = []

    user_name_query = select(UserSetting).where(UserSetting.setting == "user_name")
    user_name_result = await db.execute(user_name_query)
    user_name = user_name_result.fetchall()

    user_names_by_id = {}
    for name in user_name[0]:
        user_names_by_id[name.user_id] = json.loads(name.value)["name"]

    for user in users[0]:
        user_list_computed.append(
            GetAllUsersUser(
                id=user.id,
                organisation=user.org_id,
                role=user.role_id,
                nids=user.nids_sid,
                name=user_names_by_id[user.id],
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

    return user_list_computed


async def _get_user(auth: Auth, db: Session, userID: str) -> GetAllUsersUser:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(User).where(User.id == userID)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    user_name_query = select(UserSetting).where(UserSetting.setting == "user_name", UserSetting.user_id == userID)
    user_name_result = await db.execute(user_name_query)
    user_name = user_name_result.scalar_one_or_none()

    if user_name is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User name not found")

    return GetAllUsersUser(
        id=user.id,
        organisation=user.org_id,
        role=user.role_id,
        nids=user.nids_sid,
        name=user_name.value,
        email=user.email,
        last_login=user.last_login,
        created=user.date_created,
        totp=user.totp,
        contact=user.contactalert,
        notification=user.notification_daily or user.notification_weekly or user.notification_monthly,
        gpg_key=user.gpgkey,
        terms=user.termsaccepted,
    )


async def _delete_user(user_id: int, auth: Auth, db: Session) -> None:
    if user_id != auth.user_id and not await check_permissions(db, auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = _get_user(auth, db, str(user_id))
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()


async def _delete_user_token(auth: Auth, db: Session, userID: str) -> None:
    return None


async def _update_user(auth: Auth, db: Session, userID: str, body: UserAttributesBody) -> UserWithName:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await db.get(User, userID)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    name_result = await db.execute(
        select(UserSetting).where(UserSetting.setting == "user_name" and UserSetting.user_id == user.id)
    )

    name = name_result.scalars().first()

    if not name:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User name not found")

    settings = body.dict()

    for key in settings.keys():
        if key == "name" and settings[key] is not None:
            name.value = json.dumps({"name": str(settings[key])})
            await db.commit()
            await db.refresh(name)
        elif settings[key] is not None:
            setattr(user, key, settings[key])

    await db.commit()
    await db.refresh(user)

    user_schema = UserSchema(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        autoalert=user.autoalert,
        invited_by=user.invited_by,
        gpgkey=user.gpgkey,
        certif_public=user.certif_public,
        termsaccepted=user.termsaccepted,
        role_id=user.role_id,
        change_pw=user.change_pw == 1,
        contactalert=user.contactalert,
        disabled=user.disabled,
        expiration=user.expiration,
        current_login=user.current_login,
        last_login=user.last_login,
        force_logout=user.force_logout,
        date_created=user.date_created,
        date_modified=user.date_modified,
        external_auth_required=user.external_auth_required,
        external_auth_key=user.external_auth_key,
        last_api_access=user.last_api_access,
        notification_daily=user.notification_daily,
        notification_weekly=user.notification_weekly,
        notification_monthly=user.notification_monthly,
        totp=user.totp,
        hotp_counter=user.hotp_counter,
        last_pw_change=user.last_pw_change,
    )

    user_return = UserWithName(user=user_schema, name=json.loads(name.value)["name"])

    return user_return
