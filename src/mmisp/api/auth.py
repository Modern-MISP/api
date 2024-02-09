from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException
from mmisp.db.models.role import Role
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
        role_id: int | None = None,
        is_worker: bool | None = False,
    ) -> None:
        self.user_id = user_id
        self.org_id = org_id
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

        if not check_permissions(user_id, permissions):
            raise HTTPException(401)

        user: User = db.get(User, user_id)

        return Auth(user.id, user.org_id, user.role_id)

    return authorizer


def check_permissions(user_id: str, permissions: list[Permission] = []) -> bool:
    db = get_db()

    role: Role | None = db.query(Role).join(User, Role.id == User.role_id).filter(User.id == user_id).first()

    if not role:
        return False

    if role.perm_site_admin:
        return True

    for permission in permissions:
        if (
            (permission == Permission.ADD and (not role.perm_add or not role.perm_admin))
            or (permission == Permission.MODIFY and (not role.perm_modify or not role.perm_admin))
            or (permission == Permission.MODIFY_ORG and (not role.perm_modify_org or not role.perm_admin))
            or (permission == Permission.PUBLISH and (not role.perm_publish or not role.perm_admin))
            or (permission == Permission.DELEGATE and not role.perm_delegate)
            or (permission == Permission.SYNC and not role.perm_sync)
            or (permission == Permission.ADMIN and not role.perm_admin)
            or (permission == Permission.AUDIT and not role.perm_audit)
            or (permission == Permission.FULL and not role.perm_full)
            or (permission == Permission.AUTH and not role.perm_auth)
            or (permission == Permission.SITE_ADMIN and not role.perm_site_admin)
            or (permission == Permission.REGEXP_ACCESS and not role.perm_regexp_access)
            or (permission == Permission.TAGGER and not role.perm_tagger)
            or (permission == Permission.TEMPLATE and not role.perm_template)
            or (permission == Permission.SHARING_GROUP and not role.perm_sharing_group)
            or (permission == Permission.TAG_EDITOR and not role.perm_tag_editor)
            or (permission == Permission.SIGHTING and not role.perm_sighting)
            or (permission == Permission.OBJECT_TEMPLATE and not role.perm_object_template)
            or (permission == Permission.PUBLISH_ZMQ and not role.perm_publish_zmq)
            or (permission == Permission.PUBLISH_KAFKA and not role.perm_publish_kafka)
            or (permission == Permission.DECAYING and not role.perm_decaying)
            or (permission == Permission.GALAXY_EDITOR and not role.perm_galaxy_editor)
            or (permission == Permission.WARNINGLIST and not role.perm_warninglist)
            or (permission == Permission.VIEW_FEED_CORRELATIONS and not role.perm_view_feed_correlations)
        ):
            return False

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
