from time import time

import pytest
from fastapi import HTTPException

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions, encode_exchange_token
from mmisp.config import config
from mmisp.db.database import get_db
from mmisp.util.crypto import hash_auth_key
from tests.environment import environment
from tests.generators.model_generators.auth_key_generator import generate_auth_key


class TestAuthorize:
    @staticmethod
    def test_authorize_no_token() -> None:
        db = get_db()

        try:
            authorize(AuthStrategy.JWT)(db, "")
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    def test_authorize_valid_token() -> None:
        db = get_db()

        auth: Auth | None = authorize(AuthStrategy.JWT)(db, environment.site_admin_user_token)

        assert auth.user_id == environment.site_admin_user.id
        assert auth.role_id == environment.site_admin_user.role_id
        assert auth.org_id == environment.site_admin_user.org_id
        assert not auth.auth_key_id
        assert not auth.is_worker

    @staticmethod
    def test_authorize_using_exchange_token() -> None:
        db = get_db()

        exchange_token = encode_exchange_token(environment.site_admin_user.id)

        try:
            authorize(AuthStrategy.JWT)(db, exchange_token)
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    def test_authorize_valid_auth_key() -> None:
        clear_key = f"test key {time()}"

        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.site_admin_user.id
        auth_key.authkey = hash_auth_key(clear_key)

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        auth: Auth | None = authorize(AuthStrategy.API_KEY)(db, clear_key)

        assert auth.user_id == environment.site_admin_user.id
        assert auth.role_id == environment.site_admin_user.role_id
        assert auth.org_id == environment.site_admin_user.org_id
        assert auth.auth_key_id == auth_key.id
        assert not auth.is_worker

    @staticmethod
    def test_authorize_expired_auth_key() -> None:
        clear_key = f"test key {time()}"

        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.site_admin_user.id
        auth_key.authkey = hash_auth_key(clear_key)
        auth_key.expiration = time() - 10

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        try:
            authorize(AuthStrategy.API_KEY)(db, clear_key)
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    def test_authorize_using_worker_key() -> None:
        db = get_db()

        auth: Auth | None = authorize(AuthStrategy.WORKER_KEY)(db, config.WORKER_KEY)

        assert not auth.user_id
        assert not auth.role_id
        assert not auth.org_id
        assert not auth.auth_key_id
        assert auth.is_worker


class TestCheckPermissions:
    @staticmethod
    def test_check_permissions_site_admin() -> None:
        auth = Auth(
            user_id=environment.site_admin_user.id,
            org_id=environment.site_admin_user.org_id,
            role_id=environment.site_admin_user.role_id,
        )

        assert check_permissions(
            auth,
            [
                Permission.ADD,
                Permission.MODIFY,
                Permission.MODIFY_ORG,
                Permission.PUBLISH,
                Permission.ADMIN,
                Permission.SITE_ADMIN,
            ],
        )

    @staticmethod
    def test_check_permissions_no_write_access() -> None:
        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.site_admin_user.id
        auth_key.read_only = True

        db.add(auth_key)
        db.commit()
        db.refresh(auth_key)

        auth = Auth(
            user_id=environment.site_admin_user.id,
            org_id=environment.site_admin_user.org_id,
            role_id=environment.site_admin_user.role_id,
            auth_key_id=auth_key.id,
        )

        assert not check_permissions(auth, [Permission.WRITE_ACCESS])
