from fastapi import APIRouter

from mmisp.api_schemas.user_settings.delete_user_setting_response import DeleteUserSettingResponse
from mmisp.api_schemas.user_settings.get_get_id_user_setting_response import GetUserSettingResponse
from mmisp.api_schemas.user_settings.search_user_setting_body import SearchUserSettingBody
from mmisp.api_schemas.user_settings.search_user_setting_response import SearchUserSettingResponse
from mmisp.api_schemas.user_settings.set_user_setting_body import SetUserSettingBody
from mmisp.api_schemas.user_settings.set_user_setting_response import SetUserSettingResponse
from mmisp.api_schemas.user_settings.view_user_setting_response import ViewUserSettingResponse

router = APIRouter(tags=["user_settings"])


# Sets User Setting
@router.post("/user_settings/setSetting/{userId}/{userSettingName}")
async def set_user_settings(user_setting_in: SetUserSettingBody) -> SetUserSettingResponse:
    return SetUserSettingResponse()


# Get User Setting by Id
@router.get("/user_settings/{UserSettingsId}")
async def view_user_settings() -> ViewUserSettingResponse:
    return ViewUserSettingResponse()


# Get User Setting by ID
@router.get("/user_settings/{userid}/{userSettingName}")
async def get_auth_key_by_id() -> GetUserSettingResponse:
    return GetUserSettingResponse()


# Search all User Settings
@router.post("/user_settings")
async def search_user_settings(user_setting_in: SearchUserSettingBody) -> list[GetUserSettingResponse]:
    return SearchUserSettingResponse()


# Returns all User Settings
@router.get("/user_settings")
async def get_user_settings() -> list[GetUserSettingResponse]:  # Request Body into brackets
    return GetUserSettingResponse()  # return body in after return


# Delete AuthKey by ID
@router.delete("/user_settings/{userSettingsId}")
async def delete_user_settings() -> DeleteUserSettingResponse:
    return DeleteUserSettingResponse()


# --> deprecated


# Get User Setting by Id
@router.get("/user_settings/view/{UserSettingsId}", deprecated=True)  # Deprecated
async def view_user_settings_depr() -> ViewUserSettingResponse:
    return ViewUserSettingResponse()


# Get User Setting by IDs
@router.get("/user_settings/getSetting/{userId}/{userSettingName}", deprecated=True)  # should be without getSetting
async def get_auth_key_by_id_depr() -> GetUserSettingResponse:
    return GetUserSettingResponse()


# Delete AuthKey by ID
@router.delete("/user_settings/delete/{userSettingsId}", deprecated=True)  # Deprecated
async def delete_user_settings_depr() -> DeleteUserSettingResponse:
    return DeleteUserSettingResponse()
