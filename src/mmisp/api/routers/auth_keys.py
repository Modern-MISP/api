import json
import string
import time
from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Tuple

from fastapi import APIRouter, Depends, HTTPException, Path, status
from nanoid import generate  # type: ignore

from mmisp.lib.logger import alog, log

if TYPE_CHECKING:
    from sqlalchemy import Row
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.auth_keys import (
    AddAuthKeyBody,
    AddAuthKeyResponse,
    AddAuthKeyResponseAuthKey,
    EditAuthKeyBody,
    EditAuthKeyResponseCompl,
    EditAuthKeyResponseCompleteAuthKey,
    EditAuthKeyResponseUser,
    SearchAuthKeyBody,
    SearchGetAuthKeysResponse,
    SearchGetAuthKeysResponseAuthKey,
    SearchGetAuthKeysResponseItem,
    SearchGetAuthKeysResponseItemAuthKey,
    SearchGetAuthKeysResponseItemUser,
    ViewAuthKeyResponseWrapper,
    ViewAuthKeysResponse,
)
from mmisp.api_schemas.responses.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret
from mmisp.util.uuid import is_uuid

router = APIRouter(tags=["auth_keys"])


@router.post(
    "/auth_keys/{userId}",
    status_code=status.HTTP_201_CREATED,
    response_model=AddAuthKeyResponse,
    summary="Add an AuthKey.",
)
@alog
async def auth_keys_add_user(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    body: AddAuthKeyBody,
) -> AddAuthKeyResponse:
    """Create an AuthKey for a specific user and save it in the database.

    args:

    - the user's authentification status

    - the current database

    - the id of the user

    - the request body

    returns:

    - the added authkey
    """
    return await _auth_key_add(auth=auth, db=db, user_id=user_id, body=body)


@router.get(
    "/auth_keys/view/{AuthKeyId}",
    response_model=ViewAuthKeysResponse,
    summary="View an AuthKey",
)
@alog
async def auth_keys_view_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> ViewAuthKeysResponse:
    """View an AuthKey by its ID.

    args:

    - the user's authentification status

    - the current database

    - the id of the authkey

    returns:

    - the authkey
    """
    return await _auth_keys_view(auth=auth, db=db, auth_key_id=auth_key_id)


@router.post(
    "/auth_keys",
    response_model=list[SearchGetAuthKeysResponseItem],
    summary="Search for specific AuthKeys.",
)
@alog
async def search_auth_keys(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SearchAuthKeyBody,
) -> list[SearchGetAuthKeysResponseItem]:
    """Search for specific AuthKeys by parameters.

    args:

    - the user's authentification status

    - the current database

    - the request body

    returns:

    - the authkeys
    """
    return await _search_auth_keys(auth=auth, db=db, body=body)


@router.put(
    "/auth_keys/{AuthKeyId}",
    response_model=EditAuthKeyResponseCompl,
    summary="Edit an AuthKey.",
)
@alog
async def auth_keys_edit_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
    body: EditAuthKeyBody,
) -> EditAuthKeyResponseCompl:
    """Edit an AuthKey by its ID.

    args:

    - the user's authentification status

    - the current database

    - the id of the authkey

    - the request body

    returns:

    - the updated authkey
    """
    return await _auth_keys_edit(auth=auth, db=db, auth_key_id=auth_key_id, body=body)


@router.delete(
    "/auth_keys/{AuthKeyId}",
    response_model=StandardStatusIdentifiedResponse,
    summary="Delete given AuthKey.",
)
@alog
async def auth_keys_delete_auth_key(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> StandardStatusIdentifiedResponse:
    """Delete AuthKey by AuthKeyId from the database.

    args:

    - the user's authentification status

    - the current database

    - the id of the authkey

    returns:

    - the response from the api after the deleting request
    """
    await _auth_keys_delete(auth=auth, db=db, auth_key_id=auth_key_id)

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="AuthKey deleted.",
        message="AuthKey deleted.",
        url=f"/auth_keys/{auth_key_id}",
        id=auth_key_id,
    )


@router.get(
    "/auth_keys",
    response_model=list[SearchGetAuthKeysResponse],
    summary="Returns AuthKeys.",
)
@alog
async def auth_keys_get(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[SearchGetAuthKeysResponse]:
    """Returns all AuthKeys stored in the database as a List.

    args:

    - the user's authentification status

    - the current database

    returns:

    - all authkeys as a list
    """
    return await _auth_keys_get(auth=auth, db=db)


@router.get(
    "/auth_keys/viewOwn",
    summary="View own AuthKeys",
)
@alog
async def auth_keys_view_own_auth_keys(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[SearchGetAuthKeysResponseItem]:
    """View own Authkeys.

    args:

    - the user's authentification status

    - the current database

    - the id of the user

    returns:

    - the auth keys
    """
    return await _auth_keys_view_own(auth=auth, db=db)


#  --- deprecated ---


@router.get(
    "/auth_keys/index/{userId}",
    deprecated=True,
    summary="View own AuthKeys",
)
@alog
async def auth_keys_view_own_auth_keys_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[SearchGetAuthKeysResponse]:
    """Deprecated. View own Authkeys by the old route.

    args:

    - the user's authentification status

    - the current database

    - the id of the user

    returns:

    - the auth keys
    """
    return await _auth_keys_view_own_depr(auth=auth, db=db)


@router.post(
    "/auth_keys/add/{userId}",
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
    response_model=AddAuthKeyResponse,
    summary="Add an AuthKey.",
)
@alog
async def auth_keys_add_user_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(alias="userId")],
    body: AddAuthKeyBody,
) -> AddAuthKeyResponse:
    """Create an AuthKey for a specific user and write it to the database.

    args:

    - the user's authentification status

    - the current database

    - the id of the user

    - the request body

    returns:

    - the added authkey
    """
    return await _auth_key_add(auth=auth, db=db, user_id=user_id, body=body)


@router.post(
    "/auth_keys/edit/{AuthKeyId}",
    deprecated=True,
    response_model=EditAuthKeyResponseCompl,
    summary="Edit AuthKey",
)
@alog
async def auth_keys_edit_auth_key_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
    body: EditAuthKeyBody,
) -> EditAuthKeyResponseCompl:
    """Edit AuthKey by AuthKey ID.

    args:

    - the user's authentification status

    - the current database

    - the id of the authkey

    - the request body

    returns:

    - the updated authkey
    """
    return await _auth_keys_edit(auth=auth, db=db, auth_key_id=auth_key_id, body=body)


@router.post(
    "/auth_keys/delete/{AuthKeyId}",
    deprecated=True,
    response_model=StandardStatusIdentifiedResponse,
    summary="Delete given AuthKey.",
)
@alog
async def auth_keys_delete_auth_key_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    auth_key_id: Annotated[int, Path(alias="AuthKeyId")],
) -> StandardStatusIdentifiedResponse:
    """Delete AuthKey by AuthKeyId from the database.

    args:

    - the user's authentification status

    - the current database

    - the id of the authkey

    returns:

    - the response from the api after the deleting request
    """
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


@alog
async def _auth_key_add(auth: Auth, db: Session, user_id: int, body: AddAuthKeyBody) -> AddAuthKeyResponse:
    if body.uuid and not is_uuid(body.uuid):
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if body.user_id is not None:
        user_id = body.user_id

    if auth.user_id != user_id and not check_permissions(auth, [Permission.SITE_ADMIN]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    auth_key_string = generate(size=40, alphabet=string.ascii_letters + string.digits)
    hashed_auth_key = hash_secret(auth_key_string)

    expiration_int = parse_date(str(body.expiration)) if body.expiration else None

    auth_key = AuthKey(
        uuid=body.uuid,
        read_only=body.read_only,
        user_id=user_id,
        comment=body.comment,
        allowed_ips=json.dumps(body.allowed_ips) if body.allowed_ips else None,
        authkey=hashed_auth_key,
        authkey_start=auth_key_string[:4],
        authkey_end=auth_key_string[-4:],
        created=int(time.time()),
        expiration=expiration_int,
    )

    db.add(auth_key)

    await db.flush()
    await db.refresh(auth_key)
    return AddAuthKeyResponse(
        AuthKey=AddAuthKeyResponseAuthKey(
            id=auth_key.id,
            uuid=auth_key.uuid,
            authkey_start=auth_key.authkey_start,
            authkey_end=auth_key.authkey_end,
            created=auth_key.created,
            expiration=auth_key.expiration,
            read_only=auth_key.read_only,
            user_id=auth_key.user_id,
            comment=auth_key.comment,
            allowed_ips=json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            unique_ips=json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
            authkey_raw=auth_key_string,
        )
    )


@alog
async def _auth_keys_view(
    auth: Auth,
    db: Session,
    auth_key_id: int,
) -> ViewAuthKeysResponse:
    if not auth:
        raise HTTPException(401)

    result = await db.execute(select(AuthKey).filter(AuthKey.id == auth_key_id))
    auth_key: AuthKey | None = result.scalars().first()

    if not auth_key:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user: User | None = await db.get(User, auth_key.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return ViewAuthKeysResponse(
        AuthKey=ViewAuthKeyResponseWrapper(
            id=auth_key.id,
            uuid=auth_key.uuid,
            authkey_start=auth_key.authkey_start,
            authkey_end=auth_key.authkey_end,
            created=auth_key.created,
            expiration=auth_key.expiration,
            read_only=auth_key.read_only,
            user_id=auth_key.user_id,
            comment=auth_key.comment,
            allowed_ips=json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            unique_ips=json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
        ),
        User=SearchGetAuthKeysResponseItemUser(
            id=user.id,
            email=user.email,
        ),
    )


@alog
async def _search_auth_keys(
    auth: Auth,
    db: Session,
    body: SearchAuthKeyBody,
) -> list[SearchGetAuthKeysResponseItem]:
    query = select(AuthKey, User).join(User, AuthKey.user_id == User.id)

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
        query = query.filter(AuthKey.created == body.created)
    if body.expiration:
        query = query.filter(AuthKey.expiration == body.expiration)
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

    result = await db.execute(query.limit(body.limit).offset((body.page - 1) * body.limit))
    auth_keys_and_users: Sequence[Row[Tuple[AuthKey, User]]] = result.all()
    auth_keys_computed: list[SearchGetAuthKeysResponseItem] = []

    for auth_key_and_user in auth_keys_and_users:
        auth_keys_computed.append(
            SearchGetAuthKeysResponseItem(
                AuthKey=SearchGetAuthKeysResponseItemAuthKey(
                    id=auth_key_and_user.AuthKey.id,
                    uuid=auth_key_and_user.AuthKey.uuid,
                    authkey_start=auth_key_and_user.AuthKey.authkey_start,
                    authkey_end=auth_key_and_user.AuthKey.authkey_end,
                    created=auth_key_and_user.AuthKey.created,
                    expiration=auth_key_and_user.AuthKey.expiration,
                    read_only=auth_key_and_user.AuthKey.read_only,
                    user_id=auth_key_and_user.AuthKey.user_id,
                    comment=auth_key_and_user.AuthKey.comment,
                    allowed_ips=json.loads(auth_key_and_user.AuthKey.allowed_ips)
                    if auth_key_and_user.AuthKey.allowed_ips
                    else None,
                    unique_ips=json.loads(auth_key_and_user.AuthKey.unique_ips)
                    if auth_key_and_user.AuthKey.unique_ips
                    else [],
                ),
                User=SearchGetAuthKeysResponseItemUser(
                    id=auth_key_and_user.User.id,
                    email=auth_key_and_user.User.email,
                ),
            )
        )

    return auth_keys_computed


@alog
async def _search_auth_keys_depr(
    auth: Auth,
    db: Session,
    body: SearchAuthKeyBody,
) -> list[SearchGetAuthKeysResponse]:
    query = select(AuthKey, User).join(User, AuthKey.user_id == User.id)

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
        query = query.filter(AuthKey.created == body.created)
    if body.expiration:
        query = query.filter(AuthKey.expiration == body.expiration)
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

    result = await db.execute(query.limit(body.limit).offset((body.page - 1) * body.limit))
    auth_keys_and_users: Sequence[Row[Tuple[AuthKey, User]]] = result.all()
    auth_keys_computed: list[SearchGetAuthKeysResponse] = []

    for auth_key_and_user in auth_keys_and_users:
        auth_keys_computed.append(
            SearchGetAuthKeysResponse(
                AuthKey=SearchGetAuthKeysResponseAuthKey(
                    id=auth_key_and_user.AuthKey.id,
                    uuid=auth_key_and_user.AuthKey.uuid,
                    authkey_start=auth_key_and_user.AuthKey.authkey_start,
                    authkey_end=auth_key_and_user.AuthKey.authkey_end,
                    created=auth_key_and_user.AuthKey.created,
                    expiration=auth_key_and_user.AuthKey.expiration,
                    read_only=auth_key_and_user.AuthKey.read_only,
                    user_id=auth_key_and_user.AuthKey.user_id,
                    comment=auth_key_and_user.AuthKey.comment,
                    allowed_ips=json.loads(auth_key_and_user.AuthKey.allowed_ips)
                    if auth_key_and_user.AuthKey.allowed_ips
                    else None,
                    unique_ips=json.loads(auth_key_and_user.AuthKey.unique_ips)
                    if auth_key_and_user.AuthKey.unique_ips
                    else [],
                ),
                User=SearchGetAuthKeysResponseItemUser(
                    id=auth_key_and_user.User.id,
                    email=auth_key_and_user.User.email,
                ),
            )
        )

    return auth_keys_computed


@alog
async def _auth_keys_edit(auth: Auth, db: Session, auth_key_id: int, body: EditAuthKeyBody) -> EditAuthKeyResponseCompl:
    auth_key: AuthKey | None = await db.get(AuthKey, auth_key_id)

    if not auth_key or (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or auth_key.user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user: User | None = await db.get(User, auth_key.user_id)

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    update = body.model_dump(exclude_unset=True)
    update["allowed_ips"] = json.dumps(body.allowed_ips) if body.allowed_ips else None

    if body.expiration == "":
        update["expiration"] = None

    auth_key.patch(**update)

    await db.flush()
    await db.refresh(auth_key)
    await db.refresh(user)
    return EditAuthKeyResponseCompl(
        AuthKey=EditAuthKeyResponseCompleteAuthKey(
            id=auth_key.id,
            uuid=auth_key.uuid,
            authkey_start=auth_key.authkey_start,
            authkey_end=auth_key.authkey_end,
            created=auth_key.created,
            expiration=auth_key.expiration,
            read_only=auth_key.read_only,
            user_id=auth_key.user_id,
            comment=auth_key.comment,
            allowed_ips=json.loads(auth_key.allowed_ips) if auth_key.allowed_ips else None,
            unique_ips=json.loads(auth_key.unique_ips) if auth_key.unique_ips else [],
        ),
        User=EditAuthKeyResponseUser(
            id=user.id,
            org_id=user.org_id,
        ),
    )


@alog
async def _auth_keys_delete(auth: Auth, db: Session, auth_key_id: int) -> None:
    auth_key: AuthKey | None = await db.get(AuthKey, auth_key_id)
    if auth_key is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user: User | None = await db.get(User, auth_key.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not auth_key or (
        auth_key.user_id != auth.user_id
        and (not check_permissions(auth, [Permission.ADMIN]) or user.org_id != auth.org_id)
        and (not check_permissions(auth, [Permission.SITE_ADMIN]))
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(auth_key)
    await db.flush()


@alog
async def _auth_keys_get(
    auth: Auth,
    db: Session,
) -> list[SearchGetAuthKeysResponse]:
    query = select(AuthKey, User).join(User, AuthKey.user_id == User.id)

    if not check_permissions(auth, [Permission.SITE_ADMIN]):
        query = query.filter(User.org_id == auth.org_id)
    if not check_permissions(auth, [Permission.ADMIN]):
        query = query.filter(AuthKey.user_id == auth.user_id)

    result = await db.execute(query)
    auth_keys_and_users: Sequence[Any] = result.all()

    auth_keys_computed: list[SearchGetAuthKeysResponse] = []

    for auth_key_and_user in auth_keys_and_users:
        auth_keys_computed.append(
            SearchGetAuthKeysResponse(
                AuthKey=SearchGetAuthKeysResponseAuthKey(
                    id=auth_key_and_user.AuthKey.id,
                    uuid=auth_key_and_user.AuthKey.uuid,
                    authkey_start=auth_key_and_user.AuthKey.authkey_start,
                    authkey_end=auth_key_and_user.AuthKey.authkey_end,
                    created=auth_key_and_user.AuthKey.created,
                    expiration=auth_key_and_user.AuthKey.expiration,
                    read_only=auth_key_and_user.AuthKey.read_only,
                    user_id=auth_key_and_user.AuthKey.user_id,
                    comment=auth_key_and_user.AuthKey.comment,
                    allowed_ips=json.loads(auth_key_and_user.AuthKey.allowed_ips)
                    if auth_key_and_user.AuthKey.allowed_ips
                    else None,
                    unique_ips=json.loads(auth_key_and_user.AuthKey.unique_ips)
                    if auth_key_and_user.AuthKey.unique_ips
                    else [],
                ),
                User=SearchGetAuthKeysResponseItemUser(
                    id=auth_key_and_user.User.id,
                    email=auth_key_and_user.User.email,
                ),
            )
        )

    return auth_keys_computed


@alog
async def _auth_keys_view_own(auth: Auth, db: Session) -> list[SearchGetAuthKeysResponseItem]:
    own_key = await _search_auth_keys(auth, db, SearchAuthKeyBody(user_id=auth.user_id))
    if own_key is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return own_key


@alog
async def _auth_keys_view_own_depr(auth: Auth, db: Session) -> list[SearchGetAuthKeysResponse]:
    own_key = await _search_auth_keys_depr(auth, db, SearchAuthKeyBody(user_id=auth.user_id))
    if own_key is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return own_key


@log
def parse_date(date_str: str) -> int:
    if len(date_str) != 10 or date_str[4] != "-" or date_str[7] != "-":
        raise ValueError("Date must be in the format yyyy-mm-dd")

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format")

    unix_timestamp = int(dt.timestamp())
    return unix_timestamp
