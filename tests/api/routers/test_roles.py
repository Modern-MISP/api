def test_roles_get(client):
    response = client.get("/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    response_json = response.json()
    for role in response_json:
        assert "id" in role
        assert "name" in role
        assert "created" in role
        assert "modified" in role
        assert "perm_add" in role
        assert "perm_modify" in role
        assert "perm_modify_org" in role
        assert "perm_publish" in role
        assert "perm_delegate" in role
        assert "perm_sync" in role
        assert "perm_admin" in role
        assert "perm_audit" in role
        assert "perm_auth" in role
        assert "perm_site_admin" in role
        assert "perm_regexp_access" in role
        assert "perm_tagger" in role
        assert "perm_template" in role
        assert "perm_sharing_group" in role
        assert "perm_tag_editor" in role
        assert "perm_sighting" in role
        assert "perm_object_template" in role
        assert "default_role" in role
        assert "memory_limit" in role
        assert "max_execution_time" in role
        assert "restricted_to_site_admin" in role
        assert "perm_publish_zmq" in role
        assert "perm_publish_kafka" in role
        assert "perm_decaying" in role
        assert "enforce_rate_limit" in role
        assert "rate_limit_count" in role
        assert "perm_galaxy_editor" in role
        assert "perm_warninglist" in role
        assert "perm_view_feed_correlations" in role
        assert "perm_analyst_data" in role
        assert "permission" in role
        assert "permission_description" in role
        assert "default" in role
