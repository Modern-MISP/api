from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from . import user
from ..schemas.auth_key_schema import AuthKey


router = APIRouter(prefix="/auth_keys")


# query and return a list of existing authkey objects and associated users
@router.get("/")
async def auth_keys_get():  # Request Body into brackets
    return {AuthKey(), user.User()}  # return body in after return


# search auth keys
@router.post("/")
async def auth_keys_post(
    authkey: AuthKey,
):
    return AuthKey(), user.User()


# Add Auth Keys
# might want to revise the route, contrary to Pflichtenheft I might have messed up here.
@router.post("/add/{UserId}")
async def auth_keys_add_User(UserId: str, authKey: AuthKey):
    return AuthKey()


# View AuthKey by AuthKeyId
@router.get("/view/{AuthKeyId}")
async def auth_keys_view_AuthKey():
    return AuthKey()


# Edit AuthKey by ID
@router.put("/edit/{AuthKeyId}")
async def auth_keys_edit_AuthKey():
    return AuthKey()


# Delete AuthKey by ID
@router.delete("/{AuthKeyId}")
async def auth_keys_delete_AuthKey():
    return AuthKey()
