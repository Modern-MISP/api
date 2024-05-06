from time import time
from typing import Any

import pytest
from fastapi import HTTPException
from nanoid import generate

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions, encode_exchange_token
from mmisp.api.config import config
from mmisp.db.database import get_db
from mmisp.util.crypto import hash_secret
from tests.environment import environment
from tests.generators.model_generators.auth_key_generator import generate_auth_key


class TestAuth:
    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_no_token() -> None:
        db = get_db()

        try:
            await authorize(AuthStrategy.JWT)(db=db, authorization="")
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_valid_token() -> None:
        db = get_db()

        auth: Auth | Any = await authorize(AuthStrategy.JWT)(db=db, authorization=environment.site_admin_user_token)

        assert auth.user_id == environment.site_admin_user.id
        assert auth.role_id == environment.site_admin_user.role_id
        assert auth.org_id == environment.site_admin_user.org_id
        assert not auth.auth_key_id
        assert not auth.is_worker

    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_using_exchange_token() -> None:
        db = get_db()

        exchange_token = encode_exchange_token(environment.site_admin_user.id)

        try:
            await authorize(AuthStrategy.JWT)(db=db, authorization=exchange_token)
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_valid_auth_key() -> None:
        clear_key = generate(size=40)

        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.site_admin_user.id
        auth_key.authkey = hash_secret(clear_key)
        auth_key.authkey_start = clear_key[:4]
        auth_key.authkey_end = clear_key[-4:]

        db.add(auth_key)

        await db.commit()
        await db.refresh(auth_key)

        auth: Auth | Any = await authorize(AuthStrategy.API_KEY)(db=db, authorization=clear_key)

        assert auth.user_id == environment.site_admin_user.id
        assert auth.role_id == environment.site_admin_user.role_id
        assert auth.org_id == environment.site_admin_user.org_id
        assert auth.auth_key_id == auth_key.id
        assert not auth.is_worker

    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_expired_auth_key() -> None:
        clear_key = generate(size=40)

        db = get_db()

        auth_key = generate_auth_key()
        auth_key.user_id = environment.site_admin_user.id
        auth_key.authkey = hash_secret(clear_key)
        auth_key.authkey_start = clear_key[:4]
        auth_key.authkey_end = clear_key[-4:]
        auth_key.expiration = time() - 10

        db.add(auth_key)

        await db.commit()
        await db.refresh(auth_key)

        try:
            await authorize(AuthStrategy.API_KEY)(db=db, authorization=clear_key)
            pytest.fail()
        except HTTPException:
            pass

    @staticmethod
    @pytest.mark.asyncio
    async def test_authorize_using_worker_key() -> None:
        db = get_db()

        auth: Auth | Any = await authorize(AuthStrategy.WORKER_KEY)(db=db, authorization=config.WORKER_KEY)

        assert not auth.user_id
        assert not auth.role_id
        assert not auth.org_id
        assert not auth.auth_key_id
        assert auth.is_worker


class TestCheckPermissions:
    @staticmethod
    @pytest.mark.asyncio
    async def test_check_permissions_site_admin() -> None:
        auth = Auth(
            user_id=environment.site_admin_user.id,
            org_id=environment.site_admin_user.org_id,
            role_id=environment.site_admin_user.role_id,
        )

        assert await check_permissions(
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
