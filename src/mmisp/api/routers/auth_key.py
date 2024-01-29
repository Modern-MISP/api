from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mmisp.api_schemas.auth_key.add_auth_key_in import AuthKeyAdd
from mmisp.api_schemas.auth_key.add_auth_key_out import AuthKey
from mmisp.api_schemas.auth_key.delete_auth_key_out import AuthKeyDeleteSchema
from mmisp.api_schemas.auth_key.edit_auth_key_in import AuthKeyEdit
from mmisp.api_schemas.auth_key.edit_auth_key_out import AuthKeyEditSchema
from mmisp.api_schemas.auth_key.search_auth_keys_in import AuthKeySearch
from mmisp.api_schemas.auth_key.search_get_all_auth_keys_users_out import AuthKeyGetSchema
from mmisp.api_schemas.auth_key.view_auth_key_out import AuthKeyViewSchema
from mmisp.db.database import get_db

router = APIRouter(tags=["auth_keys"])


# Add Auth Keys
# might want to revise the route, contrary to Pflichtenheft I might have messed up here.
@router.post("/auth_keys/add/{UserId}")
async def auth_keys_add_User(UserId: str, auth_key_in: AuthKeyAdd) -> AuthKey:
    return AuthKey()


# View AuthKey by AuthKeyId
@router.get("/auth_keys/view/{AuthKeyId}")
async def auth_keys_view_AuthKey() -> AuthKeyViewSchema:
    return AuthKeyViewSchema()


# search auth keys
@router.post("/auth_keys")
async def auth_keys_post(authkey: AuthKeySearch) -> AuthKeyGetSchema:
    return AuthKeyGetSchema()


# Edit AuthKey by ID
@router.put("/auth_keys/edit/{AuthKeyId}")  # Should be without edit in route
async def auth_keys_edit_AuthKey(auth_key_in: AuthKeyEdit) -> AuthKeyEditSchema:
    return AuthKeyEditSchema()


# Delete AuthKey by ID
@router.delete("/auth_keys/{AuthKeyId}")
async def auth_keys_delete_AuthKey() -> AuthKeyDeleteSchema:
    return AuthKeyDeleteSchema()


# query and return a list of existing authkey objects and associated users
@router.get("/auth_keys", response_model=List[AuthKeyGetSchema])
async def auth_keys_get(db: Session = Depends(get_db)) -> List[AuthKeyGetSchema]:  # Request Body into brackets
    try:
        auth_keys = db.query(AuthKeyGetSchema).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Return of User still missing. Will be implemented later.
    return {auth_keys}  # return body in after return

#  ->> deprecated


# Edit AuthKeys
@router.post("/auth_keys/edit/{AuthKeyId}", deprecated=True)  # deprecated
async def auth_keys_edit_AuthKey(auth_key_in: AuthKeyEdit) -> AuthKeyEditSchema:
    return AuthKeyEditSchema()
