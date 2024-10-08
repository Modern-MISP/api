from time import time
from typing import Any

import pytest
from fastapi import HTTPException
from icecream import ic

from mmisp.api.auth import (
    Auth,
    AuthStrategy,
    Permission,
    authorize,
    check_permissions,
    decode_exchange_token,
    encode_exchange_token,
    encode_token,
)
from mmisp.api.config import config
from mmisp.db.database import get_db


@pytest.mark.asyncio
async def test_authorize_no_token(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    try:
        await authorize(AuthStrategy.JWT)(db=adb, authorization="")
        pytest.fail()
    except HTTPException:
        pass


@pytest.mark.asyncio
async def test_authorize_valid_token(db, site_admin_user_token, site_admin_user) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)
    auth: Auth | Any = await authorize(AuthStrategy.JWT)(db=adb, authorization=site_admin_user_token)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert not auth.auth_key_id
    assert not auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_using_exchange_token(site_admin_user) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    exchange_token = encode_exchange_token(site_admin_user.id)

    try:
        await authorize(AuthStrategy.JWT)(db=adb, authorization=exchange_token)
        pytest.fail()
    except HTTPException:
        pass

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_valid_auth_key(db, site_admin_user, auth_key) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    clear_key, auth_key = auth_key

    auth: Auth | Any = await authorize(AuthStrategy.API_KEY)(db=adb, authorization=clear_key)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert auth.auth_key_id == auth_key.id
    assert not auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_expired_auth_key(db, auth_key) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    clear_key, auth_key = auth_key
    auth_key.expiration = time() - 10

    await db.commit()

    try:
        await authorize(AuthStrategy.API_KEY)(db=adb, authorization=clear_key)
        pytest.fail()
    except HTTPException:
        pass

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_using_worker_key(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    auth: Auth | Any = await authorize(AuthStrategy.WORKER_KEY)(db=adb, authorization=config.WORKER_KEY)

    assert not auth.user_id
    assert not auth.role_id
    assert not auth.org_id
    assert not auth.auth_key_id
    assert auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_check_permissions_site_admin(site_admin_user) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    auth = Auth(
        user=site_admin_user,
        user_id=site_admin_user.id,
        org_id=site_admin_user.org_id,
        role_id=site_admin_user.role_id,
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

    ["" async for _ in it_db]


@pytest.mark.asyncio
def test_encode_token(site_admin_user) -> None:
    token = encode_token(site_admin_user.id)
    assert token


@pytest.mark.asyncio
def test_decode_exchange_token(site_admin_user) -> None:
    token = encode_exchange_token(site_admin_user.id)
    user_id = decode_exchange_token(token)
    assert user_id == site_admin_user.id


@pytest.mark.asyncio
async def test_authorize_readonly_route(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    try:
        await authorize(AuthStrategy.API_KEY, is_readonly_route=True)(db=adb, authorization="readonly_key")
        pytest.fail()
    except HTTPException:
        pass

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_api_key_verification_failure(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    try:
        await authorize(AuthStrategy.API_KEY)(db=adb, authorization="invalid_key")
        pytest.fail()
    except HTTPException:
        pass

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_all_strategy_with_api_key(db, site_admin_user, auth_key) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    clear_key, auth_key = auth_key

    auth: Auth | Any = await authorize(AuthStrategy.ALL)(db=adb, authorization=clear_key)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert auth.auth_key_id == auth_key.id
    assert not auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_jwt_decoding_failure(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    try:
        await authorize(AuthStrategy.JWT)(db=adb, authorization="invalid_token")
        pytest.fail()
    except HTTPException:
        pass

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_hybrid_strategy_with_jwt(db, site_admin_user_token, site_admin_user) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)
    auth: Auth | Any = await authorize(AuthStrategy.HYBRID)(db=adb, authorization=site_admin_user_token)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert not auth.auth_key_id
    assert not auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_hybrid_strategy_with_api_key(db, site_admin_user, auth_key) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    clear_key, auth_key = auth_key

    auth: Auth | Any = await authorize(AuthStrategy.HYBRID)(db=adb, authorization=clear_key)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert auth.auth_key_id == auth_key.id
    assert not auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_all_strategy_with_worker_key(db) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)

    auth: Auth | Any = await authorize(AuthStrategy.ALL)(db=adb, authorization=config.WORKER_KEY)

    assert not auth.user_id
    assert not auth.role_id
    assert not auth.org_id
    assert not auth.auth_key_id
    assert auth.is_worker

    ["" async for _ in it_db]


@pytest.mark.asyncio
async def test_authorize_all_strategy_with_jwt(db, site_admin_user_token, site_admin_user) -> None:
    it_db = get_db()
    adb = await anext(it_db)
    ic(adb)
    auth: Auth | Any = await authorize(AuthStrategy.ALL)(db=adb, authorization=site_admin_user_token)

    assert auth.user_id == site_admin_user.id
    assert auth.role_id == site_admin_user.role_id
    assert auth.org_id == site_admin_user.org_id
    assert not auth.auth_key_id
    assert not auth.is_worker

    ["" async for _ in it_db]
