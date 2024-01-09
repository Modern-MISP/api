from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import user
from app.schemas.auth_key.auth_key_schema import (AuthKey)
from ..database import get_db


router = APIRouter(prefix="/auth_keys")


# query and return a list of existing authkey objects and associated users
@router.get("/", response_model=List[AuthKey])
async def auth_keys_get(db: Session = Depends(get_db)) -> List[AuthKey]:  # Request Body into brackets
    try:
        auth_keys = db.query(AuthKey).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) #Return of User still missing. Will be implemented later.
    return {auth_keys}  # return body in after return


# search auth keys
@router.post("/")
async def auth_keys_post(
    authkey: AuthKey
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
