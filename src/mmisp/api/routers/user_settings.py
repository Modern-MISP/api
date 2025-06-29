import json
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.responses.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.user_settings import (
    GetUserSettingResponse,
    SearchUserSettingBody,
    SetUserSettingBody,
    SetUserSettingResponse,
    SetUserSettingResponseUserSetting,
    UserSettingResponse,
    UserSettingSchema,
    ViewUserSettingResponse,
    ViewUserSettingResponseUserSetting,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.user_setting import SettingName, UserSetting
from mmisp.lib.logger import alog

router = APIRouter(tags=["user_settings"])


@router.post(
    "/user_settings/setSetting/me/{userSettingName}",
    summary="Set user setting.",
)
@alog
async def set_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    # user_id: Annotated[int, Path(alias="userId")],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
    body: SetUserSettingBody,
) -> SetUserSettingResponse:
    """
    Create or Update a UserSetting by user ID and UserSettingName. \
    If specified UserSetting doesn't exist, it is created.

    Args:
      auth: Authentication details
      db: Database session
      user_id: ID of the user for whom setting is to be set
      user_setting_name: Name of the user setting to
      body: SetUserSettingBody, Data for setting the user setting

    returns:
      Response indicating success or failure
    """
    if auth.user_id is not None:
        return await _set_user_settings(
            auth=auth, db=db, user_id=auth.user_id, user_setting_name=user_setting_name, body=body
        )
    return await _set_user_settings(auth=auth, db=db, user_id=1, user_setting_name=user_setting_name, body=body)


@router.get(
    "/user_settings/{userSettingId}",
    summary="View UserSetting by ID.",
)
@alog
async def view_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> ViewUserSettingResponse:
    """
    Displays a UserSetting by the UserSettingID.

    args:

    - userSettingId: ID of the user setting to view

    - auth: Authentication details

    - db: Database session

    returns:

    - ViewUserSettingResponse: Response with details of the viewed user setting
    """
    return await _view_user_settings(auth=auth, db=db, user_setting_id=user_setting_id)


@router.get(
    "/user_settings/me/{userSettingName}",
    summary="View UserSetting.",
)
@alog
async def get_user_setting_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
) -> ViewUserSettingResponse:
    """
    Displays a UserSetting by given userID and UserSetting name.

    args:

    - userId: ID of the user for whom setting is to be viewed

    - userSettingName: Name of the user setting to view

    - auth: Authentication details

    - db: Database session

    returns:

    - ViewUserSettingResponse: Response with details of the viewed user setting
    """
    if auth.user_id is not None:
        return await _get_user_setting_by_id(
            auth=auth, db=db, user_id=auth.user_id, user_setting_name=user_setting_name
        )

    return await _get_user_setting_by_id(auth=auth, db=db, user_id=1, user_setting_name=user_setting_name)


@router.post(
    "/user_settings",
    summary="Displays all UserSettings.",
)
@alog
async def search_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchUserSettingBody,
) -> list[UserSettingResponse]:
    """
    Displays all UserSettings by specified parameters.

    args:

    - body: SearchUserSettingBody, Data for searching user settings

    - auth: Authentication details

    - db: Database session

    returns:

    - list[UserSettingResponse]: List of UserSettingResponse objects
    """
    return await _search_user_settings(auth=auth, db=db, body=body)


@router.get(
    "/user_settings",
    summary="Displays all UserSettings.",
)
@alog
async def get_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[UserSettingResponse]:
    """
    Displays all UserSettings.

    args:

    - auth: Authentication details

    - db: Database session

    returns:

    - list[UserSettingResponse]: List of UserSettingResponse objects
    """
    return await _get_user_settings(auth=auth, db=db)


@router.delete(
    "/user_settings/{userSettingId}",
    summary="Deletes a UserSetting.",
)
@alog
async def delete_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes UserSetting by UserSetting ID.

    args:

    - userSettingId: ID of the user setting to delete

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusIdentifiedResponse: Response indicating success or failure
    """
    await _delete_user_settings(auth=auth, db=db, user_setting_id=user_setting_id)

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Setting deleted.",
        message="Setting deleted.",
        url=f"/user_settings/{user_setting_id}",
        id=user_setting_id,
    )


# --- deprecated ---


@router.get(
    "/user_settings/view/{userSettingId}",
    deprecated=True,
    summary="View UserSetting by ID.",
)
@alog
async def view_user_settings_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> ViewUserSettingResponse:
    """
    Deprecated. View UserSetting by UserSettingID.

    args:

    - userSettingId: ID of the user setting to view

    - auth: Authentication details

    - db: Database session

    returns:

    - ViewUserSettingResponse: Response with details of the viewed user setting
    """
    user_setting: UserSetting | None = await db.get(UserSetting, user_setting_id)

    if not user_setting or (
        user_setting.user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user_setting_out = ViewUserSettingResponseUserSetting(
        id=user_setting.id,
        setting=user_setting.setting,
        value=json.loads(user_setting.value),
        user_id=user_setting.user_id,
        timestamp=user_setting.timestamp,
    )
    return ViewUserSettingResponse(UserSetting=user_setting_out)


@router.get(
    "/user_settings/getSetting/{userId}/{userSettingName}",
    deprecated=True,
    summary="View a UserSetting.",
)
@alog
async def get_user_setting_by_ids(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
) -> GetUserSettingResponse:
    """
    Deprecated. View a UserSetting by its userID and UserSetting name.

    args:

    - userId: ID of the user for whom setting is to be viewed

    - userSettingName: Name of the user setting to view

    - auth: Authentication details

    - db: Database session

    returns:

    - GetUserSettingResponse: Response with details of the viewed user setting
    """
    result = await db.execute(
        select(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).limit(1)
    )
    user_setting: UserSetting | None = result.scalars().first()

    if not user_setting or (
        user_setting.user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return GetUserSettingResponse(
        id=user_setting.id,
        setting=user_setting.setting,
        value=json.loads(user_setting.value),
        user_id=user_setting.user_id,
        timestamp=user_setting.timestamp,
    )


@router.delete(
    "/user_settings/delete/{userSettingId}",
    deprecated=True,
    summary="Delete UserSetting.",
)
@alog
async def delete_user_settings_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, []))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> StandardStatusIdentifiedResponse:
    """
    Deprecated. Delete a UserSetting by specified UserSettingID.

    args:

    - userSettingId: ID of the user setting to delete

    - auth: Authentication details

    - db: Database session

    returns:

    - StandardStatusIdentifiedResponse: Response indicating success or failure
    """
    await _delete_user_settings(auth=auth, db=db, user_setting_id=user_setting_id)

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Setting deleted.",
        message="Setting deleted.",
        url=f"/user_settings/delete/{user_setting_id}",
        id=user_setting_id,
    )


# --- endpoint logic ---


@alog
async def _set_user_settings(
    auth: Auth,
    db: Session,
    user_id: int,
    user_setting_name: str,
    body: SetUserSettingBody,
) -> SetUserSettingResponse:
    possible_names = {setting.value for setting in SettingName}

    if user_setting_name not in possible_names:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User Setting not found. Defined user Settings are: {', '.join(possible_names)}",
        )

    if user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).limit(1)
    )
    user_setting: UserSetting | None = result.scalars().first()

    if not user_setting:
        user_setting = UserSetting(
            setting=user_setting_name,
            user_id=user_id,
            value=json.dumps(body.value),
        )

        db.add(user_setting)

    user_setting.setting = user_setting_name
    user_setting.value = json.dumps(body.value)
    user_setting.user_id = user_id

    await db.flush()
    await db.refresh(user_setting)

    user_setting_out = SetUserSettingResponseUserSetting(
        id=user_setting.id,
        setting=user_setting.setting,
        user_id=user_setting.user_id,
        value=json.loads(user_setting.value),
        timestamp=user_setting.timestamp,
    )

    return SetUserSettingResponse(UserSetting=user_setting_out)


@alog
async def _view_user_settings(
    auth: Auth,
    db: Session,
    user_setting_id: int,
) -> ViewUserSettingResponse:
    user_setting: UserSetting | None = await db.get(UserSetting, user_setting_id)

    if not user_setting or (
        user_setting.user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user_setting_out = ViewUserSettingResponseUserSetting(
        id=user_setting.id,
        setting=user_setting.setting,
        user_id=user_setting.user_id,
        value=json.loads(user_setting.value),
        timestamp=user_setting.timestamp,
    )

    return ViewUserSettingResponse(UserSetting=user_setting_out)


@alog
async def _get_user_setting_by_id(
    db: Session,
    auth: Auth,
    user_id: int,
    user_setting_name: str,
) -> ViewUserSettingResponse:
    if user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).limit(1)
    )
    user_setting: UserSetting | None = result.scalars().first()

    if not user_setting:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user_setting_out = ViewUserSettingResponseUserSetting(
        id=user_setting.id,
        setting=user_setting.setting,
        user_id=user_setting.user_id,
        value=json.loads(user_setting.value),
        timestamp=user_setting.timestamp,
    )

    return ViewUserSettingResponse(UserSetting=user_setting_out)


@alog
async def _search_user_settings(
    auth: Auth,
    db: Session,
    body: SearchUserSettingBody,
) -> list[UserSettingResponse]:
    id: int | None = int(body.id) if body.id else None
    user_id: int | None = int(body.user_id) if body.user_id else None

    query = select(UserSetting)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(UserSetting.user_id == auth.user_id)

    if id:
        query = query.filter(UserSetting.id == id)
    if body.setting:
        query = query.filter(UserSetting.setting == body.setting)
    if user_id:
        query = query.filter(UserSetting.user_id == user_id)

    result = await db.execute(query)
    user_settings: Sequence[UserSetting] = result.scalars().all()

    user_settings_out: list[UserSettingResponse] = []

    for user_setting in user_settings:
        user_settings_out.append(
            UserSettingResponse(
                UserSetting=UserSettingSchema(
                    id=user_setting.id,
                    setting=user_setting.setting,
                    user_id=user_setting.user_id,
                    value=json.loads(user_setting.value),
                    timestamp=user_setting.timestamp,
                )
            )
        )

    return user_settings_out


@alog
async def _get_user_settings(
    auth: Auth,
    db: Session,
) -> list[UserSettingResponse]:
    query = select(UserSetting)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(UserSetting.user_id == auth.user_id)

    result = await db.execute(query)
    user_settings: Sequence[UserSetting] = result.scalars().all()

    user_settings_out: list[UserSettingResponse] = []

    for user_setting in user_settings:
        user_settings_out.append(
            UserSettingResponse(
                UserSetting=UserSettingSchema(
                    id=user_setting.id,
                    setting=user_setting.setting,
                    user_id=user_setting.user_id,
                    value=json.loads(user_setting.value),
                    timestamp=user_setting.timestamp,
                )
            )
        )

    return user_settings_out


@alog
async def _delete_user_settings(
    auth: Auth,
    db: Session,
    user_setting_id: int,
) -> None:
    user_setting: UserSetting | None = await db.get(UserSetting, user_setting_id)

    if not user_setting or (
        user_setting.user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(user_setting)
    await db.flush()
