from pydantic import BaseModel
from typing import List, Annotated
from fastapi import APIRouter

class UserSettings(BaseModel):
    id: str = ""
    setting: str = ""
    value: dict = {
        "widget": str,
        "postition": {
            "x": int,
            "y": int,
            "width": int,
            "height":int
        }
    }
    user_id: str = ""
    timestamp: str = ""

router = APIRouter(prefix="/user_settings")

#Returns all User Settings
@router.get("/")
async def get_user_settings():  # Request Body into brackets
    return {UserSettings()}  # return body in after return

#Search all User Settings
@router.post("/")
async def search_user_settings():
    return {UserSettings()}

#Get User Setting by Id
@router.get("/{UserSettingsId}")
async def view_user_settings():
    return UserSettings()

#Sets User Setting
@router.post("/setSetting/{userId/{userSettingName}")
async def set_user_settings():
    return UserSettings()

#Get User Setting by ID
@router.get("/getSetting/{userId}/{userSettingName}")
async def get_auth_key_by_id():
    return UserSettings

#Delete AuthKey by ID
@router.delete("/{userSettingsId")
async def delete_user_settings():
    return {"saved": bool,
            "success": bool,
            "name": str,
            "message": str,
            "url": str}
