import pytest

from sqlalchemy.future import select
from sqlalchemy import delete

from mmisp.db.models.role import Role
from mmisp.lib.permissions import Permission


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
async def test_role_get_with_specific_data(client, site_admin_user_token, random_test_role):
    headers = {"authorization": site_admin_user_token}
    
    response = client.get(f"/roles/{42}", headers=headers)
    role_id = random_test_role.id
    
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    
    response_json = response.json()
    role_data = response_json["Role"]

    assert role_data["id"] == role_id
    assert role_data["name"] == "test_role"
    assert role_data["perm_add"] is False
    assert role_data["perm_modify"] is False
    assert role_data["perm_modify_org"] is False
    assert role_data["perm_publish"] is False
    assert role_data["perm_delegate"] is False
    assert role_data["perm_sync"] is False
    assert role_data["perm_admin"] is False
    assert role_data["perm_audit"] is False
    assert role_data["perm_auth"] is False
    assert role_data["perm_site_admin"] is False
    assert role_data["perm_regexp_access"] is False
    assert role_data["perm_tagger"] is False
    assert role_data["perm_template"] is False
    assert role_data["perm_sharing_group"] is False
    assert role_data["perm_tag_editor"] is False
    assert role_data["perm_sighting"] is False
    assert role_data["perm_object_template"] is False
    assert role_data["default_role"] is False
    assert role_data["memory_limit"] == ""
    assert role_data["max_execution_time"] == ""
    assert role_data["restricted_to_site_admin"] is False
    assert role_data["perm_publish_zmq"] is False
    assert role_data["perm_publish_kafka"] is False
    assert role_data["perm_decaying"] is False
    assert role_data["enforce_rate_limit"] is False
    assert role_data["rate_limit_count"] == 0
    assert role_data["perm_galaxy_editor"] is False
    assert role_data["perm_warninglist"] is False
    assert role_data["perm_view_feed_correlations"] is False


@pytest.mark.asyncio
async def test_role_not_found(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/roles/{999999}", headers=headers)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_role_success(client, site_admin_user_token, db):
    headers = {"authorization": site_admin_user_token}

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

    result = await db.execute(select(Role).where(Role.name == "new_role"))
    role = result.scalar_one_or_none()

    assert role is not None


@pytest.mark.asyncio
async def test_add_role_missing_body(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}

    response = client.post(
        "/admin/roles/add",
        headers=headers,
        json=None
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_role_success(client, site_admin_user_token, random_test_role, db):
    role_id = random_test_role.id 
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{42}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["saved"] is True
    assert response_json["success"] is True
    assert response_json["name"] == "Role deleted"
    assert response_json["message"] == "Role deleted"
    assert response_json["id"] == role_id


@pytest.mark.asyncio
async def test_delete_role_not_found(client, site_admin_user_token):
    role_id = 999999
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{999999}", headers=headers)
    
    assert response.status_code == 404
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} not found."


@pytest.mark.asyncio
async def test_delete_default_role(client, site_admin_user_token, role_read_only, db):
    role_id = role_read_only.id  # ID of read only - default role
    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{7}", headers=headers)
    
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} is the default role. Can't be deleted"

    result = await db.execute(select(Role).where(Role.id == 7))
    role = result.scalar_one_or_none()

    assert role is not None


@pytest.mark.asyncio
async def test_delete_role_in_use(client, site_admin_user_token, random_test_user, random_test_role, db):
    role_id = 42

    headers = {"authorization": site_admin_user_token}
    
    response = client.delete(f"/admin/roles/delete/{42}", headers=headers)
    
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} cannot be deleted because it is assigned to one or more users."

    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    assert role is not None


@pytest.mark.asyncio
async def test_update_role_success(client, site_admin_user_token, random_test_role, db):
    headers = {"authorization": site_admin_user_token}

    role_id = random_test_role.id

    update_data = {
        "name": "updated_role_name",
        "memory_limit": "42MB"
    }

    response = client.put(
        f"/admin/roles/edit/{42}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["updated"] is True
    assert response_json["message"] == f"Role with ID {role_id} successfully updated."
    assert response_json["role"]["name"] == "updated_role_name"
    assert response_json["role"]["memory_limit"] == "42MB"


@pytest.mark.asyncio
async def test_update_role_not_found(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}

    role_id = 999999

    update_data = {
        "name": "updated_role_name"
    }

    response = client.put(
        f"/admin/roles/edit/{999999}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} not found."


@pytest.mark.asyncio
async def test_update_role_no_changes(client, site_admin_user_token, random_test_role):
    headers = {"authorization": site_admin_user_token}

    update_data = {
        "name": None,
    }

    response = client.put(
        f"/admin/roles/edit/{42}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"] == "At least one new attribute must be provided to update the role."


@pytest.mark.asyncio
async def test_update_role_missing_body(client, site_admin_user_token, role_read_only):
    headers = {"authorization": site_admin_user_token}

    response = client.put(
        f"/admin/roles/edit/{7}",
        json=None,
        headers=headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reinstate_role_success(client, site_admin_user_token, db, role_read_only):
    role_id = role_read_only.id
    headers = {"authorization": site_admin_user_token}
    
    await db.execute(delete(Role).where(Role.id == role_id))
    await db.commit()
    
    response = client.post(f"/roles/reinstate/{7}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["message"] == f"Role with ID {role_id} has been reinstated."
    assert response_json["id"] == role_id
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    assert role is not None


@pytest.mark.asyncio
async def test_reinstate_role_already_exists(client, site_admin_user_token, db, test_standard_role):
    role_id = test_standard_role.id
    headers = {"authorization": site_admin_user_token}
    
    role = await db.execute(select(Role).where(Role.id == role_id))
    role = role.scalar_one_or_none()
    assert role is not None 
    
    response = client.post(f"/roles/reinstate/{5}", headers=headers)
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} is already in use."


@pytest.mark.asyncio
async def test_reinstate_role_not_standard_role(client, site_admin_user_token, random_test_role):
    role_id = random_test_role.id 
    headers = {"authorization": site_admin_user_token}

    response = client.post(f"/roles/reinstate/{42}", headers=headers)
    assert response.status_code == 400
    
    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {role_id} is not a standard role and cannot be reinstated."


@pytest.mark.asyncio
async def test_reinstate_role_former_default_role(client, site_admin_user_token, db, role_read_only):
    role_id = role_read_only.id 
    headers = {"authorization": site_admin_user_token}
    
    await db.execute(delete(Role).where(Role.id == role_id))
    await db.commit()
    
    response = client.post(f"/roles/reinstate/{7}", headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["message"] == f"Role with ID {role_id} has been reinstated."
    
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    assert role is not None
    assert role.default_role is False


@pytest.mark.asyncio
async def test_filter_roles_success(client, site_admin_user_token, role_read_only, test_standard_role, db):

    headers = {"authorization": site_admin_user_token}

    filter_data = {
        "permissions": [Permission.ADD, Permission.SYNC]
    }

    response = client.post(
        "/roles/restSearch",
        json=filter_data,
        headers=headers 
    )

    assert response.status_code == 200

    response_json = response.json()

    assert len(response_json) == 2 # test_standard_role and another thrird role, that is misterously in the dp
    # if I filter out all roles except roles with id 5 and 7 (the two abover) during the endpoint logic it works fine

@pytest.mark.asyncio
async def test_filter_roles_no_results(client, site_admin_user_token, role_read_only, test_standard_role, db):

    headers = {"authorization": site_admin_user_token}

    filter_data = {
        "permissions": [Permission.ADMIN]
    }

    response = client.post(
        "/roles/restSearch",
        json=filter_data,
        headers=headers  
    )

    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json) == 1 # The another thrird role, that is misterously in the dp
    # if I filter out all roles except roles with id 5 and 7 (the two abover) during the endpoint logic it works fine


@pytest.mark.asyncio
async def test_filter_roles_no_permissions(client, site_admin_user_token, role_read_only, test_standard_role, db):
    headers = {"authorization": site_admin_user_token}

    body = {
        "permissions": []
    }

    response = client.post(
        "/roles/restSearch",
        json=body,
        headers=headers
    )

    assert response.status_code == 400

    response_json = response.json()
    assert response_json["detail"] == "No permissions provided for filtering."


@pytest.mark.asyncio
async def test_get_users_by_role_success(client, site_admin_user_token, random_test_user, random_test_role):
    user_id = random_test_user.id
    role_id = random_test_role.id
    headers = {"authorization": site_admin_user_token}

    response = client.post(f"/admin/roles/users/{42}", headers=headers)

    assert response.status_code == 200
    users = response.json()
    
    assert isinstance(users, list)
    assert any(user["id"] == user_id for user in users)


@pytest.mark.asyncio
async def test_get_users_by_role_no_users(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}

    response = client.post(f"/admin/roles/users/{42}", headers=headers)

    assert response.status_code == 200
    users = response.json()
    
    assert users == []


@pytest.mark.asyncio
async def test_get_users_by_role_not_found(client, site_admin_user_token):
    headers = {"authorization": site_admin_user_token}

    response = client.post(f"/admin/roles/users/{999999}", headers=headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_set_default_role_success(client, site_admin_user_token, random_test_role, role_read_only, db):
    role_id = random_test_role.id
    headers = {"authorization": site_admin_user_token}

    response = client.put(
        f"/admin/roles/setDefault/{role_id}",
        headers=headers
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["success"] is True
    assert response_json["name"] == "Default Role Changed"
    assert response_json["message"] == f"The default role has been changed to {random_test_role.name}."
    assert response_json["id"] == role_id


@pytest.mark.asyncio
async def test_set_default_role_role_not_found(client, site_admin_user_token):
    non_existent_role_id = 999999
    headers = {"authorization": site_admin_user_token}

    response = client.put(
        f"/admin/roles/setDefault/{999999}",
        headers=headers
    )

    assert response.status_code == 404

    response_json = response.json()
    assert response_json["detail"] == f"Role with ID {non_existent_role_id} not found."


@pytest.mark.asyncio
async def test_set_default_role_already_set(client, site_admin_user_token, role_read_only):
    headers = {"authorization": site_admin_user_token}

    response = client.put(
        f"/admin/roles/setDefault/{7}",
        headers=headers
    )

    assert response.status_code == 400
    

"""  
endpoint edit_user_role is now edit_user_role_depr -> No tests needed anymore!

@pytest.mark.asyncio
async def test_edit_user_role_success(client, site_admin_user_token, role_read_only, db, random_test_user):
    user_id = random_test_user.id
    headers = {"authorization": site_admin_user_token}
    body = {"role_id": 7} 

    response = client.put(f"/admin/users/edit/{user_id}", json=body, headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    
    assert response_json["message"] == "User's role has been updated to Role 7"
    assert response_json["id"] == user_id
    assert response_json["Role"] == "test_read_only"
    

@pytest.mark.asyncio
async def test_edit_user_role_missing_role_id(client, site_admin_user_token, random_test_user):
    user_id = random_test_user.id
    headers = {"authorization": site_admin_user_token}
    body = {}  

    response = client.put(f"/admin/users/edit/{user_id}", json=body, headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_edit_user_role_nonexistent_role(client, site_admin_user_token, random_test_user):
    user_id =random_test_user.id
    headers = {"authorization": site_admin_user_token}
    body = {"role_id": 31415}

    response = client.put(f"/admin/users/edit/{user_id}", json=body, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Role with ID 31415 not found."
"""
