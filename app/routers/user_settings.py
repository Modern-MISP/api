from fastapi import APIRouter

from app.schemas.user_setting.user_setting_schema import UserSettings

router = APIRouter(prefix="/user_settings")


# Returns all User Settings
@router.get("/")
async def get_user_settings() -> UserSettings():  # Request Body into brackets
    return {UserSettings()}  # return body in after return


# Search all User Settings
@router.post("/")
async def search_user_settings() -> UserSettings():
    return {UserSettings()}


# Get User Setting by Id
@router.get("/{UserSettingsId}")
async def view_user_settings() -> UserSettings():
    return UserSettings()


# Sets User Setting
@router.post("/setSetting/{userId/{userSettingName}")
async def set_user_settings() -> UserSettings():
    return UserSettings()


# Get User Setting by ID
@router.get("/getSetting/{userId}/{userSettingName}")
async def get_auth_key_by_id() -> UserSettings():
    return UserSettings


# Delete AuthKey by ID
@router.delete("/{userSettingsId")
async def delete_user_settings() -> UserSettings():
    return {"saved": bool, "success": bool, "name": str, "message": str, "url": str}