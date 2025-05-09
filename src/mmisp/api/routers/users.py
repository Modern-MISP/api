import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.organisations import OrganisationUsersResponse
from mmisp.api_schemas.responses.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.roles import RoleUsersResponse
from mmisp.api_schemas.users import (
    AddUserBody,
    AddUserResponse,
    AddUserResponseData,
    GetUsersElement,
    GetUsersUser,
    UserAttributesBody,
    UserWithName,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.db.models.user_setting import UserSetting
from mmisp.lib.logger import alog
from mmisp.lib.settings import get_user_setting, set_user_setting
from mmisp.util.crypto import hash_secret

router = APIRouter(tags=["users"])


@router.post(
    "/users",
    summary="Add new user",
)
@alog
async def add_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddUserBody,
) -> AddUserResponse:
    """
    Adds a new user with the given details.

    args:

    - Data representing the new user to be added

    - The current database

    returns:

    - Data representing the attributes of the new user
    """
    return await _add_user(auth=auth, db=db, body=body)


@router.get("/users/view/me.json")
@router.get("/users/view/me")
@alog
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> GetUsersElement:
    """
    Retrieves information about the logged in user.

    args:

    - Authentication details of the logged in user

    returns:

    - Information about the logged in user
    """

    return await _get_user(auth, db, str(auth.user_id))


@router.get(
    "/users/view/all",
    summary="Get all users",
)
@alog
async def get_all_users(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetUsersElement]:
    """
    Retrieves a list of all users.

    args:

    - None

    returns:

    - List containing all users
    """
    return await _get_all_users(auth=auth, db=db)


@router.get(
    "/users/view/{userId}",
    summary="Get a user by id",
)
@alog
async def get_user_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
) -> GetUsersElement:
    """
    Retrieves a user specified by id.

    args:

    - ID of the user to get

    - The current database

    returns:

    - Data representing the attributes of the searched user
    """
    return await _get_user(auth, db, user_id)


@router.delete(
    "/users/{user_id}",
    summary="Delete a user",
)
@alog
async def delete_user(
    user_id: Annotated[str, Path(alias="user_id")],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes a user by their ID.

    args:

    - ID of the user to delete

    - auth: Authentication details of the current user

    - The current database

    returns:
    - StandardStatusIdentifiedResponse: Response indicating success or failure
    """
    return await _delete_user(user_id=user_id, auth=auth, db=db)


@router.delete(
    "/users/tokens/{userId}",
    # response_model=UserAttributesResponse,
    summary="Delete a users login token",
)
@alog
async def delete_user_token(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
) -> None:
    """
    Deletes a users login token by their ID.

    args:

    - ID of the user with the token to delete

    - The current database

    returns:

    - Response indicating success or failure
    """
    return await _delete_user_token(auth, db, user_id)


@router.put(
    "/users/{userId}",
    # response_model=UserAttributesResponse,
    summary="Update a user",
)
@alog
async def update_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
    body: UserAttributesBody,
) -> UserWithName:
    """
    Updates an existing user by their ID.

    args:

    - ID of the user to update

    - Updated data for the user

    - The current database

    returns:

    - Data representing the updated attributes of the user
    """
    return await _update_user(auth, db, user_id, body)


# --- deprecated ---


@router.post(
    "/admin/users/add",
    deprecated=True,
    summary="Add new user",
)
@alog
async def add_user_deprecated(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddUserBody,
) -> AddUserResponse:
    """
    Adds a new user with the given details.

    args:

    - Data representing the new user to be added

    - The current database

    returns:

    - Data representing the attributes of the new user
    """
    return await _add_user(auth=auth, db=db, body=body)


@router.put(
    "/admin/users/edit/{userId}",
    deprecated=True,
    summary="Update a user",
)
@alog
async def update_user_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
    body: UserAttributesBody,
) -> UserWithName:
    """
    Deprecated. Updates an existing user using the old route.

    args:

    - ID of the user to update

    - Updated data for the user

    - The current database

    returns:

    - Data representing the updated attributes of the user
    """
    return await _update_user(auth, db, user_id, body)


@router.get(
    "/admin/users/view/{userId}",
    deprecated=True,
    summary="Get a user by id",
)
@alog
async def get_user_by_id_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Path(alias="userId")],
) -> GetUsersElement:
    """
    Deprecated. Retrieves a user specified by id with the old route.

    args:

    - ID of the user to get

    - The current database

    returns:

    - Data representing the attributes of the searched user
    """
    return await _get_user(auth, db, user_id)


@router.get(
    "/admin/users",
    deprecated=True,
    summary="Get all users",
)
@alog
async def get_all_users_deprecated(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetUsersElement]:
    """
    Retrieves a list of all users.

    args:

    - None

    returns:

    - List containing all users
    """
    return await _get_all_users(auth=auth, db=db)


@router.delete(
    "/admin/users/delete/{userId}",
    deprecated=True,
    summary="Delete a user",
)
@alog
async def delete_user_depr(
    user_id: Annotated[str, Path(alias="userId")],
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> StandardStatusIdentifiedResponse:
    """
    Deprecated. Deletes a user by their ID with the old route.

    args:

    - ID of the user to delete

    - auth: Authentication details of the current user

    - The current database

    returns:
    - StandardStatusIdentifiedResponse: Response indicating success or failure
    """
    return await _delete_user(user_id=user_id, auth=auth, db=db)


# --- endpoint logic ---


@alog
async def _add_user(auth: Auth, db: Session, body: AddUserBody) -> AddUserResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user_result = await db.execute(select(User).where(User.email == body.email))
    if user_result.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, detail="User already exists with this email")

    org = await db.get(Organisation, body.org_id)

    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    role = await db.get(Role, body.role_id)

    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")

    user = User(
        password=hash_secret(body.password),
        org_id=org.id,
        role_id=role.id,
        email=body.email,
        authkey=body.authkey,
        invited_by=auth.user_id,
        nids_sid=body.nids_sid,
        termsaccepted=body.termsaccepted,
        change_pw=True,
        contactalert=body.contactalert,
        disabled=body.disabled,
        notification_daily=body.notification_daily,
        notification_weekly=body.notification_weekly,
        notification_monthly=body.notification_monthly,
    )

    db.add(user)

    await db.flush()
    await db.refresh(user)

    await set_user_setting(db, "user_name", user.id, json.dumps({"name": str(body.name)}))

    return AddUserResponse(User=AddUserResponseData(**user.__dict__))


@alog
async def _get_all_users(
    auth: Auth,
    db: Session,
) -> list[GetUsersElement]:
    query = select(User)

    if not (check_permissions(auth, [Permission.SITE_ADMIN]) or check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    result = await db.execute(query)
    users = result.fetchall()
    user_list_computed: list[GetUsersElement] = []

    user_names_by_id = await get_user_names_by_id(db)
    roles_by_id = await get_roles_by_id(db)
    organisations_by_id = await get_organisations_by_id(db)

    for user in users:
        user_list_computed.append(
            GetUsersElement(
                User=GetUsersUser(
                    id=user[0].id,
                    org_id=user[0].org_id,
                    server_id=user[0].server_id,
                    email=user[0].email,
                    autoalert=user[0].autoalert,
                    auth_key=user[0].authkey,
                    invited_by=user[0].invited_by,
                    gpg_key=user[0].gpgkey,
                    certif_public=user[0].certif_public,
                    nids_sid=user[0].nids_sid,
                    termsaccepted=user[0].termsaccepted,
                    newsread=user[0].newsread,
                    role_id=user[0].role_id,
                    change_pw=bool(user[0].change_pw),
                    contactalert=user[0].contactalert,
                    disabled=user[0].disabled,
                    expiration=user[0].expiration,
                    current_login=user[0].current_login,
                    last_login=user[0].last_login,
                    last_api_access=user[0].last_api_access,
                    force_logout=user[0].force_logout,
                    date_created=user[0].date_created,
                    date_modified=user[0].date_modified,
                    last_pw_change=user[0].last_pw_change,
                    name=user_names_by_id.get(user[0].id, user[0].email),
                    totp=(user[0].totp is not None),
                    contact=user[0].contactalert,
                    notification=(
                        user[0].notification_daily or user[0].notification_weekly or user[0].notification_monthly
                    ),
                ),
                Role=RoleUsersResponse(**roles_by_id[user[0].role_id].asdict()),
                Organisation=OrganisationUsersResponse(
                    id=user[0].org_id,
                    name=organisations_by_id[user[0].org_id].name,
                ),
            )
        )

    return user_list_computed


@alog
async def get_user_names_by_id(db: Session) -> dict:
    user_name_query = select(UserSetting).where(UserSetting.setting == "user_name")
    user_name_result = await db.execute(user_name_query)
    user_name = user_name_result.fetchall()

    user_names_by_id = {}
    for name in user_name:
        user_names_by_id[name[0].user_id] = json.loads(name[0].value)["name"]
    return user_names_by_id


@alog
async def get_roles_by_id(db: Session) -> dict:
    roles_query = select(Role)
    roles_result = await db.execute(roles_query)
    roles = roles_result.fetchall()

    roles_by_id = {}
    for role in roles:
        roles_by_id[role[0].id] = role[0]
    return roles_by_id


@alog
async def get_organisations_by_id(db: Session) -> dict:
    organisations_query = select(Organisation)
    organisations_result = await db.execute(organisations_query)
    organisations = organisations_result.fetchall()

    organisations_by_id = {}
    for organisation in organisations:
        organisations_by_id[organisation[0].id] = organisation[0]
    return organisations_by_id


@alog
async def _get_user(auth: Auth, db: Session, userID: str) -> GetUsersElement:
    if not (
        check_permissions(auth, [Permission.SITE_ADMIN])
        or check_permissions(auth, [Permission.ADMIN])
        or str(auth.user_id) == userID
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(User).where(User.id == userID)

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    user_settings_query = select(UserSetting).where(UserSetting.user_id == userID)
    user_settings_result = await db.execute(user_settings_query)
    user_settings = user_settings_result.scalars().all()

    user_settings_dict = {}

    for setting in user_settings:
        user_settings_dict[setting.setting] = json.loads(setting.value)

    if user_settings_dict.get("user_name") is None:
        user_settings_dict["user_name"] = {"name": user.email}

    if user_settings is None or user_settings_dict.get("user_name") is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User name not found")

    role_query = select(Role).where(Role.id == user.role_id)
    role_result = await db.execute(role_query)
    role = role_result.scalar_one_or_none()

    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")

    organisation_query = select(Organisation).where(Organisation.id == user.org_id)
    organisation_result = await db.execute(organisation_query)
    organisation = organisation_result.scalar_one_or_none()

    if organisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    return GetUsersElement(
        User=GetUsersUser(
            id=user.id,
            org_id=user.org_id,
            server_id=user.server_id,
            email=user.email,
            autoalert=user.autoalert,
            auth_key=user.authkey,
            invited_by=user.invited_by,
            gpg_key=user.gpgkey,
            certif_public=user.certif_public,
            nids_sid=user.nids_sid,
            termsaccepted=user.termsaccepted,
            newsread=user.newsread,
            role_id=user.role_id,
            change_pw=bool(user.change_pw),
            contactalert=user.contactalert,
            disabled=user.disabled,
            expiration=user.expiration,
            current_login=user.current_login,
            last_login=user.last_login,
            last_api_access=user.last_api_access,
            force_logout=user.force_logout,
            date_created=user.date_created,
            date_modified=user.date_modified,
            last_pw_change=user.last_pw_change,
            totp=(user.totp is not None),
            hotp_counter=user.hotp_counter,
            notification_daily=user.notification_daily,
            notification_weekly=user.notification_weekly,
            notification_monthly=user.notification_monthly,
            external_auth_required=user.external_auth_required,
            external_auth_key=user.external_auth_key,
            sub=user.sub,
            name=user_settings_dict["user_name"]["name"],
            contact=user.contactalert,
            notification=(user.notification_daily or user.notification_weekly or user.notification_monthly),
        ),
        Role=RoleUsersResponse(**role.asdict()),
        Organisation=OrganisationUsersResponse(**organisation.asdict()),
        UserSetting=user_settings_dict,
    )


@alog
async def _delete_user(user_id: str, auth: Auth, db: Session) -> StandardStatusIdentifiedResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) or check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    user_settings = await db.execute(select(UserSetting).where(UserSetting.user_id == user.id))
    for setting in user_settings.scalars():
        await db.delete(setting)
        await db.flush()

    await db.delete(user)
    await db.flush()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="User deleted.",
        message="User deleted.",
        url=f"/users/{user_id}",
        id=user_id,
    )


@alog
async def _delete_user_token(auth: Auth, db: Session, userID: str) -> None:
    return None


@alog
async def _update_user(auth: Auth, db: Session, userID: str, body: UserAttributesBody) -> UserWithName:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await db.get(User, userID)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    settings = body.model_dump(exclude_unset=True)
    setting_name = settings.pop("name", None)
    if setting_name is not None:
        await set_user_setting(db, "user_name", user.id, json.dumps({"name": str(setting_name)}))
    user.patch(**settings)

    await db.flush()
    await db.refresh(user)

    user_name = await get_user_setting(db, "user_name", user.id)
    if user_name is None:
        user_name = ""
    else:
        user_name = json.loads(user_name)["name"]

    user_return = UserWithName(user=user.asdict(), name=user_name)

    return user_return
