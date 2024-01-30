from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mmisp.api_schemas.auth_keys.add_auth_key_body import AddAuthKeyBody
from mmisp.api_schemas.auth_keys.add_auth_key_response import AddAuthKeyResponse
from mmisp.api_schemas.auth_keys.delete_auth_key_response import DeleteAuthKeyResponse
from mmisp.api_schemas.auth_keys.edit_auth_key_body import EditAuthKeyBody
from mmisp.api_schemas.auth_keys.edit_auth_key_response import EditAuthKeyResponse
from mmisp.api_schemas.auth_keys.search_auth_keys_body import SearchAuthKeyBody
from mmisp.api_schemas.auth_keys.search_get_all_auth_keys_users_response import SearchGetAuthKeysReponse
from mmisp.api_schemas.auth_keys.view_auth_key_response import ViewAuthKeysResponse
from mmisp.db.database import get_db

router = APIRouter(tags=["auth_keys"])


# Add Auth Keys
# might want to revise the route, contrary to Pflichtenheft I might have messed up here.
@router.post("/auth_keys/add/{UserId}")
async def auth_keys_add_user(UserId: str, auth_key_in: AddAuthKeyBody) -> AddAuthKeyResponse:
    return AddAuthKeyResponse()


# View AuthKey by AuthKeyId
@router.get("/auth_keys/view/{AuthKeyId}")
async def auth_keys_view_auth_key() -> ViewAuthKeysResponse:
    return ViewAuthKeysResponse()


# search auth keys
@router.post("/auth_keys")
async def auth_keys_post(authkey: SearchAuthKeyBody) -> SearchGetAuthKeysReponse:
    return SearchGetAuthKeysReponse()


# Edit AuthKey by ID
@router.put("/auth_keys/edit/{AuthKeyId}")  # Should be without edit in route
async def auth_keys_edit_auth_key(auth_key_in: EditAuthKeyBody) -> EditAuthKeyResponse:
    return EditAuthKeyResponse()


# Delete AuthKey by ID
@router.delete("/auth_keys/{AuthKeyId}")
async def auth_keys_delete_auth_key() -> DeleteAuthKeyResponse:
    return DeleteAuthKeyResponse()


# query and return a list of existing authkey objects and associated users
@router.get("/auth_keys", response_model=list[SearchGetAuthKeysReponse])
async def auth_keys_get(db: Session = Depends(get_db)) -> list[SearchGetAuthKeysReponse]:  # Request Body into brackets
    try:
        auth_keys = db.query(SearchGetAuthKeysReponse).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Return of User still missing. Will be implemented later.
    return {auth_keys}  # return body in after return


#  ->> deprecated


# Edit AuthKeys
@router.post("/auth_keys/edit/{AuthKeyId}", deprecated=True)  # deprecated
async def auth_keys_edit_auth_key_legacy(auth_key_in: EditAuthKeyBody) -> EditAuthKeyResponse:
    return EditAuthKeyResponse()
