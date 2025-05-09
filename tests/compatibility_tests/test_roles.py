import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_roles(db, auth_key, client, site_admin_user_token) -> None:
    path = "/roles"
    request_body = None

    assert get_legacy_modern_diff("get", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_edit_role(db, auth_key, client, site_admin_user_token) -> None:
    path = "/admin/roles/edit/5"

    def preprocessor(modern, legacy):
        del modern["Role"]["modified"]
        del legacy["Role"]["modified"]

    request_body = {"perm_add": False, "perm_modify": False, "perm_modify_org": False, "perm_publish": False}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client, preprocessor=preprocessor) == {}


@pytest.mark.asyncio
async def test_edit_role_not_found(db, auth_key, client, site_admin_user_token) -> None:
    path = "/admin/roles/edit/314"
    request_body = None

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_role_not_found(db, auth_key, client, site_admin_user_token) -> None:
    path = "/admin/roles/delete/314"
    request_body = None

    assert get_legacy_modern_diff("delete", path, request_body, auth_key, client) == {}
