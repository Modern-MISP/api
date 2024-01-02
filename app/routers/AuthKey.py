from pydantic import BaseModel
from typing import List, Annotated
from fastapi import APIRouter
from . import User
>>>>>>> gettingROuteTOWork

class AuthKey(BaseModel):
    id: str = ""
    uuid: str = ""
    authkey_start: str = ""
    authkey_end: str = ""
    created: str = ""
    expiration: str = ""
    read_only: bool = False
    user_id: str = ""
    comment: str = ""
    allowed_ips: str = ""  # Stringified JSON Array of IP addresses
    last_used: str = ""
    unique_ips: List[str] = [""]
    authkey_raw: str = ""

router = APIRouter(prefix="/auth_keys")

<<<<<<< HEAD
>>>>>>> gettingROuteTOWork

#query and return a list of existing authkey objects and associated users
@router.get("/")
async def auth_keys_get():  # Request Body into brackets
    return {AuthKey(), User.User()}  # return body in after return

<<<<<<< HEAD
=======
#search auth keys
@router.post("/")
async def auth_keys_post(
    authkey: AuthKey,
):
    return {{AuthKey(), User.User()}}

#Add Auth Keys
#might want to revise the route, contrary to Pflichtenheft I might have messed up here.
@router.post("/add/{UserId}")
async def auth_keys_add_User(UserId: str, authKey: AuthKey):
>>>>>>> gettingROuteTOWork
    return AuthKey()

#View AuthKey by AuthKeyId
@router.get("/auth_keys/view/{AuthKeyId}")
async def auth_keys_view_AuthKey():
    return AuthKey()

#Edit AuthKey by ID
@router.put("/auth_keys/edit/{AuthKeyId}")
async def auth_keys_edit_AuthKey():
    return AuthKey()

#Delete AuthKey by ID
@router.delete("/auth_keys/{AuthKeyId}")
async def auth_keys_delete_AuthKey():
    return AuthKey()
