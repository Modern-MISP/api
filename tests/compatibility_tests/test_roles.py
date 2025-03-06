import pytest

from sqlalchemy import delete

from mmisp.db.models.role import Role
from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_roles(db, auth_key, client, site_admin_user_token) -> None:
    path = "/roles"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}

'''
@pytest.mark.asyncio
async def test_edit_role(db, auth_key, client, site_admin_user_token) -> None:
    path = "/admin/roles/edit/5"

    request_body = {"name": "updated_role_name"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}
'''
