"""
Modern MISP API - mmisp.api.auth

Handlers to manage authentication and authorization to the modern misp api.

"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from time import time
from typing import Annotated, Awaitable, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy import or_
from sqlalchemy.future import select

from mmisp.api.config import config
from mmisp.db.database import Session, get_db
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.lib.permissions import Permission
from mmisp.util.crypto import verify_secret


class AuthStrategy(StrEnum):
    """
    Possible strategies to use for authentication to the api.
    Valid values:

    - jwt: Use only jwts after login
    - api_key: Use only api-key
    - jwt/api_key: Either jwt or api_key
    - worker_key: Only accessible for modern misp worker
    - all: Use any authentication method
    """

    JWT = "jwt"
    API_KEY = "api_key"
    HYBRID = "jwt/api_key"
    WORKER_KEY = "worker_key"
    ALL = "all"


@dataclass
class Auth:
    """
    Contains the result of an authentication process.
    """

    user_id: int | None = None
    org_id: int | None = None
    role_id: int | None = None
    auth_key_id: int | None = None
    is_worker: bool | None = False


async def _get_user(
    db: Session, authorization: str, strategy: AuthStrategy, permissions: list[Permission], is_readonly_route: bool
) -> tuple[User, int | None]:
    user_id: int | None = None
    auth_key_id: int | None = None

    # check for JWT
    if strategy in [AuthStrategy.JWT, AuthStrategy.HYBRID, AuthStrategy.ALL]:
        user_id = _decode_token(authorization)

        if user_id:
            return await user_login_allowed(db, user_id, False)

    # check for API_KEY
    if strategy in [AuthStrategy.API_KEY, AuthStrategy.HYBRID, AuthStrategy.ALL]:
        res = await _check_api_key(db, authorization, is_readonly_route)

        if res:
            user_id, auth_key_id = res

            # only users with this permission are allowed to use api keys
            permissions.append(Permission.AUTH)

            return await user_login_allowed(db, user_id, True, auth_key_id)

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


async def user_login_allowed(
    db: Session, user_id: int, api_login: bool, auth_key_id: int | None = None
) -> tuple[User, int | None]:
    user = await db.get(User, user_id)
    if user is not None:
        if not api_login and user.force_logout:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User has been logged out")
        if user.disabled:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User has been disabled")

        return user, auth_key_id
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


def authorize(
    strategy: AuthStrategy, permissions: list[Permission] | None = None, is_readonly_route: bool = False
) -> Callable[[Session, str], Awaitable[Auth]]:
    if permissions is None:
        permissions = []

    async def authorizer(
        db: Annotated[Session, Depends(get_db)],
        authorization: Annotated[str, Depends(APIKeyHeader(name="authorization"))],
    ) -> Auth:
        authorization = authorization.replace("Bearer ", "")

        if not is_readonly_route and config.READONLY_MODE:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Readonly mode is active, but route is not readonly")

        if not authorization:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        # check for workers
        if strategy in [AuthStrategy.WORKER_KEY, AuthStrategy.ALL] and authorization == config.WORKER_KEY:
            return Auth(is_worker=True)

        user, auth_key_id = await _get_user(db, authorization, strategy, permissions, is_readonly_route)

        auth = Auth(user_id=user.id, org_id=user.org_id, role_id=user.role_id, auth_key_id=auth_key_id)

        if not await check_permissions(db, auth, permissions):
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        return auth

    return authorizer


async def check_permissions(db: Session, auth: Auth, permissions: list[Permission] = []) -> bool:
    result = await db.execute(select(Role).join(User, Role.id == User.role_id).filter(User.id == auth.user_id).limit(1))
    role: Role | None = result.scalars().first()

    if not role:
        return False

    permission_roles = role.get_permissions()

    for permission in permissions:
        if permission not in permission_roles:
            return False

    return True


def encode_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, config.HASH_SECRET, "HS256")


def encode_exchange_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exchange_token": True,
        "exp": datetime.utcnow() + timedelta(minutes=1),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, config.HASH_SECRET, "HS256")


def decode_exchange_token(token: str) -> str | None:
    payload: dict

    try:
        payload = jwt.decode(token, config.HASH_SECRET, ["HS256"])
    except jwt.InvalidTokenError:
        return None

    if not payload or not payload.get("exchange_token", None):
        return None

    return payload.get("user_id", None)


def _decode_token(token: str) -> int | None:
    payload: dict

    try:
        payload = jwt.decode(token, config.HASH_SECRET, ["HS256"])
    except jwt.InvalidTokenError:
        return None

    if not payload or not payload.get("user_id", None) or payload.get("exchange_token", None):
        return None

    return int(payload["user_id"])


async def _check_api_key(db: Session, authorization: str, is_readonly_route: bool) -> tuple[int, int] | None:
    result = await db.execute(
        select(AuthKey).filter(
            AuthKey.authkey_start == authorization[:4],
            AuthKey.authkey_end == authorization[-4:],
            or_(AuthKey.expiration == 0, AuthKey.expiration > int(time())),
        )
    )

    potential_auth_keys: Sequence[AuthKey] = result.scalars().all()

    for auth_key in potential_auth_keys:
        if verify_secret(authorization, auth_key.authkey):
            if auth_key.read_only and not is_readonly_route:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="API Key is readonly, but requested route is not")
            return auth_key.user_id, auth_key.id
    return None
