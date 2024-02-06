from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from mmisp.config import config
from mmisp.db.database import get_db
from mmisp.db.models.user import User


class AuthStrategy(Enum):
    JWT = "jwt"
    API_KEY = "api_key"
    HYBRID = "jwt/api_key"
    WORKER_KEY = "worker_key"
    ALL = "all"


class Permission(Enum):
    ADD = "add"
    MODIFY = "modify"
    MODIFY_ORG = "modify_org"
    PUBLISH = "publish"
    DELEGATE = "delegate"
    SYNC = "sync"
    ADMIN = "admin"
    AUDIT = "audit"
    FULL = "full"
    AUTH = "auth"
    SITE_ADMIN = "site_admin"
    REGEXP_ACCESS = "regexp_access"
    TAGGER = "tagger"
    TEMPLATE = "template"
    SHARING_GROUP = "sharing_group"
    TAG_EDITOR = "tag_editor"
    SIGHTING = "sighting"
    OBJECT_TEMPLATE = "object_template"
    PUBLISH_ZMQ = "publish_zmq"
    PUBLISH_KAFKA = "publish_kafka"
    DECAYING = "decaying"
    GALAXY_EDITOR = "galaxy_editor"
    WARNINGLIST = "warninglist"
    VIEW_FEED_CORRELATIONS = "view_feed_correlations"


class Auth:
    def __init__(
        self: "Auth",
        user_id: int | None = None,
        org_id: int | None = None,
        server_id: int | None = None,
        role_id: int | None = None,
        is_worker: bool | None = False,
    ) -> None:
        self.user_id = user_id
        self.org_id = org_id
        self.server_id = server_id
        self.role_id = role_id
        self.is_worker = is_worker


def authorize(strategy: AuthStrategy, permissions: list[Permission] = []) -> Callable[[Session, str], Auth]:
    def authorizer(db: Session = Depends(get_db), authorization: str = Header("")) -> Auth:
        authorization = authorization.replace("Bearer ", "")

        if not authorization:
            raise HTTPException(401)

        if strategy in [AuthStrategy.WORKER_KEY, AuthStrategy.ALL] and authorization == config.WORKER_KEY:
            return Auth(is_worker=True)

        user_id: str | None = None

        if strategy in [AuthStrategy.JWT, AuthStrategy.HYBRID, AuthStrategy.ALL]:
            user_id = _decode_token(authorization)

        if not user_id and strategy in [AuthStrategy.API_KEY, AuthStrategy.HYBRID, AuthStrategy.ALL]:
            user_id = _check_api_key(authorization)

            if user_id:
                permissions.append(Permission.AUTH)  # only users with this permission are allowed to use api keys

        if not user_id:
            raise HTTPException(401)

        # check_permissions(userId, permissions)

        user: User = db.get(User, user_id)

        return Auth(user.id, user.org_id, 0, user.role_id)

    return authorizer


def check_permissions(userId: str, permissions: list[Permission] = []) -> bool:
    return True


def encode_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, config.HASH_SECRET, "HS256")


def _decode_token(authorization: str) -> str | None:
    payload: dict

    try:
        payload = jwt.decode(authorization, config.HASH_SECRET, ["HS256"])
    except jwt.DecodeError:
        return None

    if not payload:
        return None

    return payload.get("user_id", None)


def _check_api_key(authorization: str) -> str | None:
    pass
