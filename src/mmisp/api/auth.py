from mmisp.db.models.user import User
from enum import Enum
from sqlalchemy.orm import Session
from mmisp.db.database import get_db
from fastapi import Depends, Header, HTTPException
from mmisp.config import config


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
        self,
        userId: int | None = None,
        orgId: int | None = None,
        roleId: int | None = None,
    ):
        self.userId = userId
        self.orgId = orgId
        self.roleId = roleId


def authorize(strategy: AuthStrategy, permissions: list[Permission] = []):
    def authorizer(db: Session = Depends(get_db), authorization: str = Header("")):
        authorization = authorization.replace("Bearer ", "")

        if not authorization:
            raise HTTPException(401)

        if (
            strategy in [AuthStrategy.WORKER_KEY, AuthStrategy.ALL]
            and authorization == config.WORKER_KEY
        ):
            return Auth()

        user: User | None = None

        if strategy in [AuthStrategy.JWT, AuthStrategy.HYBRID, AuthStrategy.ALL]:
            # TODO check jwt
            pass

        if not user and strategy in [
            AuthStrategy.API_KEY,
            AuthStrategy.HYBRID,
            AuthStrategy.ALL,
        ]:
            # TODO check apikey
            pass

        # TODO check permissions

        return Auth(0, 0, 0)

    return authorizer
