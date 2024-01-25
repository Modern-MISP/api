from fastapi import APIRouter

from mmisp.api_schemas.user_setting.delete_user_setting_out import UserSettingDelete
from mmisp.api_schemas.user_setting.get_get_id_user_setting_out import UserSettingGet
from mmisp.api_schemas.user_setting.search_user_setting_in import UserSettingSearchIn
from mmisp.api_schemas.user_setting.search_user_setting_out import UserSettingSearch
from mmisp.api_schemas.user_setting.set_user_setting_in import UserSettingSetIn
from mmisp.api_schemas.user_setting.set_user_setting_out import UserSettingSet
from mmisp.api_schemas.user_setting.view_user_setting_out import UserSettingView

router = APIRouter(tags=["user_settings"])


# Returns all User Settings
@router.get("/user_settings")
async def get_user_settings() -> list[UserSettingGet]:  # Request Body into brackets
    return UserSettingGet()  # return body in after return


# Search all User Settings
@router.post("/user_settings")
async def search_user_settings(user_setting_in: UserSettingSearchIn) -> list[UserSettingGet]:
    return UserSettingSearch()


# Get User Setting by Id
@router.get("/user_settings/view/{UserSettingsId}", deprecated=True)  # Deprecated
@router.get("/user_settings/{UserSettingsId}")
async def view_user_settings() -> UserSettingView:
    return UserSettingView()


# Sets User Setting
@router.post("/user_settings/setSetting/{userId}/{userSettingName}")
async def set_user_settings(user_setting_in: UserSettingSetIn) -> UserSettingSet:
    return UserSettingSet()


# Get User Setting by ID
@router.get("/user_settings/getSetting/{userId}/{userSettingName}")  # should be without getSetting
@router.get("/user_settings/{userid}/{userSettingName}")
async def get_auth_key_by_id() -> UserSettingGet:
    return UserSettingGet()


# Delete AuthKey by ID
@router.delete("/user_settings/{userSettingsId}")
@router.delete("/user_settings/delete/{userSettingsId}", deprecated=True)  # Deprecated
async def delete_user_settings() -> UserSettingDelete:
    return UserSettingDelete()
