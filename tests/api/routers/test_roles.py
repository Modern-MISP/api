import pytest


@pytest.mark.asyncio
async def test_roles_get(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    response = client.get("/roles", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    response_json = response.json()
    for role in response_json:
        role_data = role["Role"]
        assert "id" in role_data
        assert "name" in role_data
        assert "created" in role_data
        assert "modified" in role_data
        assert "perm_add" in role_data
        assert "perm_modify" in role_data
        assert "perm_modify_org" in role_data
        assert "perm_publish" in role_data
        assert "perm_delegate" in role_data
        assert "perm_sync" in role_data
        assert "perm_admin" in role_data
        assert "perm_audit" in role_data
        assert "perm_auth" in role_data
        assert "perm_site_admin" in role_data
        assert "perm_regexp_access" in role_data
        assert "perm_tagger" in role_data
        assert "perm_template" in role_data
        assert "perm_sharing_group" in role_data
        assert "perm_tag_editor" in role_data
        assert "perm_sighting" in role_data
        assert "perm_object_template" in role_data
        assert "default_role" in role_data
        assert "memory_limit" in role_data
        assert "max_execution_time" in role_data
        assert "restricted_to_site_admin" in role_data
        assert "perm_publish_zmq" in role_data
        assert "perm_publish_kafka" in role_data
        assert "perm_decaying" in role_data
        assert "enforce_rate_limit" in role_data
        assert "rate_limit_count" in role_data
        assert "perm_galaxy_editor" in role_data
        assert "perm_warninglist" in role_data
        assert "perm_view_feed_correlations" in role_data
        assert "perm_analyst_data" in role_data
        assert "permission" in role_data
        assert "permission_description" in role_data
        assert "default" in role_data
