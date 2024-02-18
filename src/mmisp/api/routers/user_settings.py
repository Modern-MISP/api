import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.user_settings.get_uid_user_setting_response import GetUserSettingResponse
from mmisp.api_schemas.user_settings.get_user_settings_response import UserSetting as UserSettingSchema
from mmisp.api_schemas.user_settings.get_user_settings_response import UserSettingResponse
from mmisp.api_schemas.user_settings.search_user_setting_body import SearchUserSettingBody
from mmisp.api_schemas.user_settings.set_user_setting_body import SetUserSettingBody
from mmisp.api_schemas.user_settings.set_user_setting_response import (
    SetUserSettingResponse,
    SetUserSettingResponseUserSetting,
)
from mmisp.api_schemas.user_settings.view_user_setting_response import (
    ViewUserSettingResponse,
    ViewUserSettingResponseUserSetting,
)
from mmisp.db.database import get_db
from mmisp.db.models.user_setting import SettingName, UserSetting

router = APIRouter(tags=["user_settings"])


@router.post("/user_settings/setSetting/{userId}/{userSettingName}")
async def set_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
    body: SetUserSettingBody,
) -> SetUserSettingResponse:
    return await _set_user_settings(auth=auth, db=db, user_id=user_id, user_setting_name=user_setting_name, body=body)


@router.get("/user_settings/{userSettingId}")
async def view_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> ViewUserSettingResponse:
    return await _view_user_settings(auth=auth, db=db, user_setting_id=user_setting_id)


@router.get("/user_settings/{userId}/{userSettingName}")
async def get_user_setting_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
) -> ViewUserSettingResponse:
    return await _get_user_setting_by_id(auth=auth, db=db, user_id=user_id, user_setting_name=user_setting_name)


@router.post("/user_settings")
async def search_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchUserSettingBody,
) -> list[UserSettingResponse]:
    return await _search_user_settings(auth=auth, db=db, body=body)


@router.get("/user_settings")
async def get_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[UserSettingResponse]:
    return await _get_user_settings(auth=auth, db=db)


@router.delete("/user_settings/{userSettingId}")
async def delete_user_settings(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> StandardStatusIdentifiedResponse:
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


@router.get("/user_settings/view/{userSettingId}", deprecated=True)
async def view_user_settings_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> ViewUserSettingResponse:
    user_setting: UserSetting | None = db.get(UserSetting, user_setting_id)

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


@router.get("/user_settings/getSetting/{userId}/{userSettingName}", deprecated=True)
async def get_user_setting_by_ids(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    user_setting_name: Annotated[str, Path(alias="userSettingName")],
) -> GetUserSettingResponse:
    user_setting: UserSetting | None = (
        db.query(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).first()
    )

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


@router.delete("/user_settings/delete/{userSettingId}", deprecated=True)
async def delete_user_settings_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS]))],
    db: Annotated[Session, Depends(get_db)],
    user_setting_id: Annotated[int, Path(alias="userSettingId")],
) -> StandardStatusIdentifiedResponse:
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

    user_setting: UserSetting | None = (
        db.query(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).first()
    )

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

    db.commit()
    db.refresh(user_setting)

    user_setting_out = SetUserSettingResponseUserSetting(
        id=user_setting.id,
        setting=user_setting.setting,
        user_id=user_setting.user_id,
        value=json.loads(user_setting.value),
        timestamp=user_setting.timestamp,
    )

    return SetUserSettingResponse(UserSetting=user_setting_out)


async def _view_user_settings(
    auth: Auth,
    db: Session,
    user_setting_id: int,
) -> ViewUserSettingResponse:
    user_setting: UserSetting | None = db.get(UserSetting, user_setting_id)

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


async def _get_user_setting_by_id(
    db: Session,
    auth: Auth,
    user_id: int,
    user_setting_name: str,
) -> ViewUserSettingResponse:
    if user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user_setting: UserSetting | None = (
        db.query(UserSetting).filter(UserSetting.user_id == user_id, UserSetting.setting == user_setting_name).first()
    )

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


async def _search_user_settings(
    auth: Auth,
    db: Session,
    body: SearchUserSettingBody,
) -> list[UserSettingResponse]:
    id: int | None = int(body.id) if body.id else None
    user_id: int | None = int(body.user_id) if body.user_id else None

    query = db.query(UserSetting)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(UserSetting.user_id == auth.user_id)

    if id:
        query = query.filter(UserSetting.id == id)
    if body.setting:
        query = query.filter(UserSetting.setting == body.setting)
    if user_id:
        query = query.filter(UserSetting.user_id == user_id)

    user_settings: list[UserSetting] = query.all()

    user_settings_out: list[UserSettingSchema] = []

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


async def _get_user_settings(
    auth: Auth,
    db: Session,
) -> list[UserSettingResponse]:
    query = db.query(UserSetting)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query.filter(UserSetting.user_id == auth.user_id)

    user_settings: list[UserSetting] = db.query(UserSetting).all()

    user_settings_out: list[UserSettingSchema] = []

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


async def _delete_user_settings(
    auth: Auth,
    db: Session,
    user_setting_id: int,
) -> None:
    user_setting: UserSetting | None = db.get(UserSetting, user_setting_id)

    if not user_setting or (
        user_setting.user_id != auth.user_id and not check_permissions(auth, [Permission.SITE_ADMIN])
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(user_setting)
    db.commit()
