import pytest

from sqlalchemy.future import select
from sqlalchemy import delete

from mmisp.db.models.role import Role


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


@pytest.mark.asyncio
async def test_role_get_with_specific_data(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    
    response = client.get(f"/roles/{1}", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    
    response_json = response.json()
    role_data = response_json["Role"]

    assert role_data["id"] == 1
    assert role_data["name"] == "admin"
    assert role_data["perm_add"] is True
    assert role_data["perm_modify"] is True
    assert role_data["perm_modify_org"] is True
    assert role_data["perm_publish"] is True
    assert role_data["perm_delegate"] is True
    assert role_data["perm_sync"] is True
    assert role_data["perm_admin"] is True
    assert role_data["perm_audit"] is True
    assert role_data["perm_auth"] is True
    assert role_data["perm_site_admin"] is False
    assert role_data["perm_regexp_access"] is False
    assert role_data["perm_tagger"] is True
    assert role_data["perm_template"] is True
    assert role_data["perm_sharing_group"] is True
    assert role_data["perm_tag_editor"] is True
    assert role_data["perm_sighting"] is True
    assert role_data["perm_object_template"] is False
    assert role_data["default_role"] is False
    assert role_data["memory_limit"] == ""
    assert role_data["max_execution_time"] == ""
    assert role_data["restricted_to_site_admin"] is False
    assert role_data["perm_publish_zmq"] is True
    assert role_data["perm_publish_kafka"] is True
    assert role_data["perm_decaying"] is True
    assert role_data["enforce_rate_limit"] is False
    assert role_data["rate_limit_count"] == 0
    assert role_data["perm_galaxy_editor"] is True
    assert role_data["perm_warninglist"] is False
    assert role_data["perm_view_feed_correlations"] is True


@pytest.mark.asyncio
async def test_role_not_found(client, site_admin_user_token):
    invalid_role_id = 999999  
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/roles/{invalid_role_id}", headers=headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_role_success(client, site_admin_user_token):
    headers = {"Authorization": site_admin_user_token}

    role_data = {
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
        "perm_view_feed_correlations": False
    }

    response = client.post(
        "/admin/roles/add",
        json=role_data,
        headers=headers
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["created"] is True
    assert response_json["message"] == "Role 'new_role' successfully created."
    assert "role" in response_json
    assert response_json["role"]["name"] == "new_role"


@pytest.mark.asyncio
async def test_add_role_missing_body(client, site_admin_user_token):
    headers = {"Authorization": site_admin_user_token}

    response = client.post(
        "/admin/roles/add",
        headers=headers
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "Request body cannot be None."


@pytest.mark.asyncio
async def test_delete_role_success(client, site_admin_user_token):
    role_id = 2  
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{role_id}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["saved"] is True
    assert response_json["success"] is True
    assert response_json["name"] == "Role deleted"
    assert response_json["message"] == "Role deleted"
    assert response_json["id"] == str(role_id)


@pytest.mark.asyncio
async def test_delete_role_not_found(client, site_admin_user_token):
    role_id = 999999
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{role_id}", headers=headers)
    
    assert response.status_code == 404
    
    response_json = response.json()
    assert response_json["saved"] is False
    assert response_json["name"] == "Role not found"
    assert response_json["message"] == f"Role with ID {role_id} not found."
    assert response_json["id"] == str(role_id)


@pytest.mark.asyncio
async def test_delete_default_role(client, site_admin_user_token):
    role_id = 7  # ID of read only - default role
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{role_id}", headers=headers)
    
    assert response.status_code == 404
    
    response_json = response.json()
    assert response_json["saved"] is False
    assert response_json["name"] == "Can't delete default role"
    assert response_json["message"] == f"Role with ID {role_id} is the default role. Can't be deleted"
    assert response_json["id"] == str(role_id)


@pytest.mark.asyncio
async def test_delete_role_in_use(client, site_admin_user_token):
    role_id = 1
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{role_id}", headers=headers)
    
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["saved"] is False
    assert response_json["name"] == "Role in use"
    assert response_json["message"] == f"Role with ID {role_id} cannot be deleted because it is assigned to one or more users."
    assert response_json["id"] == str(role_id)


@pytest.mark.asyncio
async def test_reinstate_role_success(client, site_admin_user_token, db):
    role_id = 2  
    headers = {"authorization": site_admin_user_token}
    
    await db.execute(delete(Role).where(Role.id == role_id))
    await db.commit()
    
    response = client.post(f"/roles/reinstate/{role_id}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["message"] == f"Role with ID {role_id} has been reinstated."
    assert response_json["id"] == role_id
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    assert role is not None


@pytest.mark.asyncio
async def test_reinstate_role_already_exists(client, site_admin_user_token, db):
    role_id = 1
    headers = {"authorization": site_admin_user_token}
    
    role = await db.execute(select(Role).where(Role.id == role_id))
    role = role.scalar_one_or_none()
    assert role is not None 
    
    response = client.post(f"/roles/reinstate/{role_id}", headers=headers)
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} is already in use."


@pytest.mark.asyncio
async def test_reinstate_role_not_standard_role(client, site_admin_user_token):
    role_id = 8 
    headers = {"authorization": site_admin_user_token}

    response = client.post(f"/roles/reinstate/{role_id}", headers=headers)
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} is not a standard role and cannot be reinstated."


@pytest.mark.asyncio
async def test_reinstate_role_former_default_role(client, site_admin_user_token, db):
    role_id = 7  
    headers = {"authorization": site_admin_user_token}
    
    await db.execute(delete(Role).where(Role.id == role_id))
    await db.commit()
    
    response = client.post(f"/roles/reinstate/{role_id}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["message"] == f"Role with ID {role_id} has been reinstated."
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    assert role is not None
    assert role.default_role is False
