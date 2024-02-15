from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from mmisp.config import config
from mmisp.db.database import get_db
from mmisp.db.models.role import Role
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
    """Manage Own Events."""
    MODIFY_ORG = "modify_org"
    """Manage Organisation Events."""
    PUBLISH = "publish"
    """Publish Organisation Events."""
    DELEGATE = "delegate"
    """Allow users to create delegation requests for their own org only events to trusted third parties."""
    SYNC = "sync"
    """Synchronisation permission, can be used to connect two MISP instances create data on behalf of other users.
    Make sure that the role with this permission has also access to tagging and tag editing rights."""
    ADMIN = "admin"
    """Limited organisation admin - create, manage users of their own organisation."""
    AUDIT = "audit"
    """Access to the audit logs of the user\'s organisation."""
    FULL = "full"
    AUTH = "auth"
    """Users with this permission have access to authenticating via their Auth keys,
    granting them access to the API."""
    SITE_ADMIN = "site_admin"
    """Unrestricted access to any data and functionality on this instance."""
    REGEXP_ACCESS = "regexp_access"
    """Users with this role can modify the regex rules affecting how data is fed into MISP.
    Make sure that caution is advised with handing out roles that include this permission,
    user controlled executed regexes are dangerous."""
    TAGGER = "tagger"
    """Users with roles that include this permission can attach
    or detach existing tags to and from events/attributes."""
    TEMPLATE = "template"
    """Create or modify templates, to be used when populating events."""
    SHARING_GROUP = "sharing_group"
    """Permission to create or modify sharing groups."""
    TAG_EDITOR = "tag_editor"
    """This permission gives users the ability to create tags."""
    SIGHTING = "sighting"
    """Permits the user to push feedback on attributes into MISP by providing sightings."""
    OBJECT_TEMPLATE = "object_template"
    """Create or modify MISP Object templates."""
    PUBLISH_ZMQ = "publish_zmq"
    """Allow users to publish data to the ZMQ pubsub channel via the publish event to ZMQ button."""
    PUBLISH_KAFKA = "publish_kafka"
    """Allow users to publish data to Kafka via the publish event to Kafka button."""
    DECAYING = "decaying"
    """Create or modify MISP Decaying Models."""
    GALAXY_EDITOR = "galaxy_editor"
    """Create or modify MISP Galaxies and MISP Galaxies Clusters."""
    WARNINGLIST = "warninglist"
    """Allow to manage warninglists."""
    VIEW_FEED_CORRELATIONS = "view_feed_correlations"
    """Allow the viewing of feed correlations. Enabling this can come at a performance cost."""


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


def _decode_token(token: str) -> str | None:
    payload: dict

    try:
        payload = jwt.decode(token, config.HASH_SECRET, ["HS256"])
    except jwt.InvalidTokenError:
        return None

    if not payload or payload.get("exchange_token", None):
        return None

    return payload.get("user_id", None)


def _check_api_key(authorization: str) -> str | None:
    pass
