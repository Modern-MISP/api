import pytest

from mmisp.tests.compatibility_helpers import get_legacy_modern_diff


@pytest.mark.asyncio
async def test_get_all_roles(db, auth_key, client, site_admin_user_token, random_test_role) -> None:
    path = "/roles"

    assert get_legacy_modern_diff("get", path, auth_key, client) == {}


"""
#I AM NOT SURE HOW THAT WORKS YET BUT WILL FIGURE IT OUT

@pytest.mark.asyncio
async def test_get_specific_role(db, auth_key, client, site_admin_user_token, role_read_only) -> None:
    path = "/roles/{6}"

    assert get_legacy_modern_diff("get", path, auth_key, client) == {}


@pytest.mark.asyncio
async def test_add_role(db, auth_key, client, site_admin_user_token) -> None:
    path = "/admin/roles/add"

    request_body = {
        "name": "new_role",
        "perm_add": True,
        "perm_modify": False,
        "perm_modify_org": False,
        "perm_publish": False,
        "perm_delegate": False,
        "perm_sync": False,
        "perm_admin": False,
        "perm_audit": False,
        "perm_auth": False,
        "perm_site_admin": False,
        "perm_regexp_access": False,
        "perm_tagger": False,
        "perm_template": False,
        "perm_sharing_group": False,
        "perm_tag_editor": False,
        "perm_sighting": False,
        "perm_object_template": False,
        "default_role": False,
        "memory_limit": "",
        "max_execution_time": "",
        "restricted_to_site_admin": False,
        "perm_publish_zmq": False,
        "perm_publish_kafka": False,
        "perm_decaying": False,
        "enforce_rate_limit": False,
        "rate_limit_count": 0,
        "perm_galaxy_editor": False,
        "perm_warninglist": False,
        "perm_view_feed_correlations": False,
    }

    assert get_legacy_modern_diff("post", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_role_success(db, auth_key, client, site_admin_user_token, random_test_role) -> None:
    path = "/admin/roles/delete/{42}"

    assert get_legacy_modern_diff("delete", path, auth_key, client) == {}


@pytest.mark.asyncio
async def test_delete_role_assigned_to_user(db, auth_key, client, site_admin_user_token, random_test_role, random_test_user) -> None:
    path = "/admin/roles/delete/{42}"

    assert get_legacy_modern_diff("delete", path, auth_key, client) == {}


@pytest.mark.asyncio
async def test_edit_role(db, auth_key, client, site_admin_user_token, random_test_role) -> None:
    path = "/admin/roles/edit/{42}"

    request_body = {"name": "updated_role_name", "memory_limit": "42MB"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


@pytest.mark.asyncio
async def test_set_default_role(db, auth_key, client, site_admin_user_token, random_test_role) -> None:
    path = "/admin/roles/setDefault/{42}"

    request_body = {"name": "updated_role_name", "memory_limit": "42MB"}

    assert get_legacy_modern_diff("put", path, request_body, auth_key, client) == {}


"""
