import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from nanoid import generate
from sqlalchemy.orm import Session

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.auth_keys.add_auth_key_body import AddAuthKeyBody
from mmisp.api_schemas.auth_keys.add_auth_key_response import AddAuthKeyResponse
from mmisp.api_schemas.auth_keys.edit_auth_key_body import EditAuthKeyBody
from mmisp.api_schemas.auth_keys.edit_auth_key_response import (
    EditAuthKeyResponse,
)
from mmisp.api_schemas.auth_keys.search_auth_keys_body import SearchAuthKeyBody
from mmisp.api_schemas.auth_keys.search_get_all_auth_keys_users_response import (
    SearchGetAuthKeysResponseItem,
)
from mmisp.api_schemas.auth_keys.view_auth_key_response import ViewAuthKeysResponse
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret
from mmisp.util.models import update_record
from mmisp.util.partial import partial
from mmisp.util.uuid import is_uuid

router = APIRouter(tags=["auth_keys"])


@router.post("/auth_keys/{userId}", status_code=status.HTTP_201_CREATED, response_model=partial(AddAuthKeyResponse))
@with_session_management
async def auth_keys_add_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    body: AddAuthKeyBody,
) -> dict:
    return await _auth_key_add(auth=auth, db=db, user_id=user_id, body=body)


@router.get("/auth_keys/view/{AuthKeyId}", response_model=partial(ViewAuthKeysResponse))
@with_session_management
async def auth_keys_view_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> dict:
    return await _auth_keys_view(auth=auth, db=db, auth_key_id=auth_key_id)


@router.post("/auth_keys", response_model=list[partial(SearchGetAuthKeysResponseItem)])
@with_session_management
async def search_auth_keys(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchAuthKeyBody,
) -> list[dict]:
    return await _search_auth_keys(auth=auth, db=db, body=body)


@router.put("/auth_keys/{AuthKeyId}", response_model=partial(EditAuthKeyResponse))
@with_session_management
async def auth_keys_edit_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
    body: EditAuthKeyBody,
) -> dict:
    return await _auth_keys_edit(auth=auth, db=db, auth_key_id=auth_key_id, body=body)


@router.delete("/auth_keys/{AuthKeyId}")
@with_session_management
async def auth_keys_delete_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> StandardStatusIdentifiedResponse:
    await _auth_keys_delete(auth=auth, db=db, auth_key_id=auth_key_id)

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="AuthKey deleted.",
        message="AuthKey deleted.",
        url=f"/auth_keys/{auth_key_id}",
        id=auth_key_id,
    )


@router.get("/auth_keys", response_model=list[partial(SearchGetAuthKeysResponseItem)])
@with_session_management
async def auth_keys_get(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return await _auth_keys_get(auth=auth, db=db)


#  --- deprecated ---


@router.post(
    "/auth_keys/add/{userId}",
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
    response_model=partial(AddAuthKeyResponse),
)
@with_session_management
async def auth_keys_add_user_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    body: AddAuthKeyBody,
) -> dict:
    return await _auth_key_add(auth=auth, db=db, user_id=user_id, body=body)


@router.post("/auth_keys/edit/{AuthKeyId}", deprecated=True, response_model=partial(EditAuthKeyResponse))
@with_session_management
async def auth_keys_edit_auth_key_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
    body: EditAuthKeyBody,
) -> dict:
    return await _auth_keys_edit(auth=auth, db=db, auth_key_id=auth_key_id, body=body)


@router.delete("/auth_keys/delete/{AuthKeyId}", deprecated=True)
@with_session_management
async def auth_keys_delete_auth_key_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID, [Permission.WRITE_ACCESS, Permission.AUTH]))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> StandardStatusIdentifiedResponse:
    await _auth_keys_delete(auth=auth, db=db, auth_key_id=auth_key_id)

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="AuthKey deleted.",
        message="AuthKey deleted.",
        url=f"/auth_keys/delete/{auth_key_id}",
        id=auth_key_id,
    )


# --- endpoint logic ---


async def _auth_key_add(auth: Auth, db: Session, user_id: int, body: AddAuthKeyBody) -> dict:
    if body.uuid and not is_uuid(body.uuid):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if body.user_id is not None:
        user_id = body.user_id

    if auth.user_id != user_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    auth_key_string = generate(size=40)
    hashed_auth_key = hash_secret(auth_key_string)

    auth_key = AuthKey(
        uuid=body.uuid,
        read_only=body.read_only,  # TODO auth refactoring
        user_id=user_id,
        comment=body.comment,
        allowed_ips=json.dumps(body.allowed_ips) if body.allowed_ips else None,
        authkey=hashed_auth_key,
        authkey_start=auth_key_string[:4],
        authkey_end=auth_key_string[-4:],
        expiration=body.expiration,
    )

    db.add(auth_key)
    db.commit()
    db.refresh(auth_key)

    return {
        "AuthKey": {
            **auth_key.__dict__,
            "allowed_ips": json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            "unique_ips": json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
            "authkey_raw": auth_key_string,
        }
    }


async def _auth_keys_view(
    auth: Auth,
    db: Session,
    auth_key_id: int,
) -> dict:
    if not auth:
        raise HTTPException(401)
    auth_key: AuthKey | None = db.query(AuthKey).filter(AuthKey.id == auth_key_id).first()

    if not auth_key or (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or auth_key.user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return {
        "AuthKey": {
            **auth_key.__dict__,
            "allowed_ips": json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            "unique_ips": json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
        },
        "User": {**auth_key.user.__dict__},
    }


async def _search_auth_keys(
    auth: Auth,
    db: Session,
    body: SearchAuthKeyBody,
) -> list[dict]:
    query = db.query(AuthKey).join(User, AuthKey.user_id == User.id)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(User.org_id == auth.org_id)
    if not check_permissions(auth, [Permission.ADMIN]):
        query = query.filter(AuthKey.user_id == auth.user_id)

    if body.id:
        query = query.filter(AuthKey.id == body.id)
    if body.uuid:
        query = query.filter(AuthKey.uuid == body.uuid)
    if body.authkey_start:
        query = query.filter(AuthKey.authkey_start == body.authkey_start)
    if body.authkey_end:
        query = query.filter(AuthKey.authkey_end == body.authkey_end)
    if body.created:
        query = query.filter(AuthKey.created == int(body.created))
    if body.expiration:
        query = query.filter(AuthKey.expiration == int(body.expiration))
    if body.read_only:
        query = query.filter(AuthKey.read_only.is_(body.read_only))
    if body.user_id:
        query = query.filter(AuthKey.user_id == int(body.user_id))
    if body.comment:
        query = query.filter(AuthKey.comment == body.comment)
    if body.allowed_ips:
        if isinstance(body.allowed_ips, list):
            body.allowed_ips = json.dumps(body.allowed_ips)

        query = query.filter(AuthKey.allowed_ips == body.allowed_ips)

    auth_keys: list[AuthKey] = query.limit(body.limit).offset(body.page * body.limit).all()

    auth_keys_computed: list[dict] = []

    for auth_key in auth_keys:
        auth_keys_computed.append(
            {
                "AuthKey": {
                    **auth_key.__dict__,
                    "allowed_ips": json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
                    "unique_ips": json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
                },
                "User": {**auth_key.user.__dict__},
            }
        )

    return auth_keys_computed


async def _auth_keys_edit(auth: Auth, db: Session, auth_key_id: int, body: EditAuthKeyBody) -> dict:
    auth_key: AuthKey | None = db.query(AuthKey).filter(AuthKey.id == auth_key_id).first()

    if not auth_key or (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or auth_key.user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update = body.dict()
    update["allowed_ips"] = json.dumps(body.allowed_ips) if body.allowed_ips else None

    update_record(auth_key, update)

    db.commit()
    db.refresh(auth_key)

    return {
        "AuthKey": {
            **auth_key.__dict__,
            "allowed_ips": json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            "unique_ips": json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
        },
        "User": {**auth_key.user.__dict__},
    }


async def _auth_keys_delete(auth: Auth, db: Session, auth_key_id: int) -> None:
    auth_key: AuthKey | None = db.get(AuthKey, auth_key_id)

    if not auth_key or (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or auth_key.user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(auth_key)
    db.commit()


async def _auth_keys_get(
    auth: Auth,
    db: Session,
) -> list[dict]:
    query = db.query(AuthKey).join(User, AuthKey.user_id == User.id)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(User.org_id == auth.org_id)
    if not check_permissions(auth, [Permission.ADMIN]):
        query = query.filter(AuthKey.user_id == auth.user_id)

    auth_keys: list[AuthKey] = query.all()

    auth_keys_computed: list[dict] = []

    for auth_key in auth_keys:
        auth_keys_computed.append(
            {
                "AuthKey": {
                    **auth_key.__dict__,
                    "allowed_ips": json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
                    "unique_ips": json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
                },
                "User": {**auth_key.user.__dict__},
            }
        )

    return auth_keys_computed
