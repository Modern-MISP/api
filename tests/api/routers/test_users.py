import json
from time import time

import pytest
from icecream import ic
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.db.models.user import User
from mmisp.db.models.user_setting import UserSetting
from mmisp.api.auth import encode_token

@pytest.fixture
def read_only_user_token(view_only_user):
    return encode_token(view_only_user.id)


def test_users_me(site_admin_user_token, site_admin_user, client) -> None:
    response = client.get("/users/view/me", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == site_admin_user.id


def test_users_create(site_admin_user_token, site_admin_user, site_admin_role, client, db) -> None:
    email = "test@automated.com" + str(time())
    name = "test_user" + str(time())

    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "authkey": "test",
            "email": email,
            "password": "test",
            "name": name,
            "role": site_admin_role.id,
            "org": site_admin_user.org_id,
            "nids_sid": "12345",
            "disabled": False,
            "contactalert": False,
            "invited_by": site_admin_user.id,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
        },
    )
    ic(response.json())
    # Check if the Status Code is 200
    json_str = response.json()
    assert response.status_code == 200
    user_id = json_str.get("User").get("id")

    # Check if the User_setting user_name is created
    query = select(UserSetting).where(UserSetting.user_id == user_id and UserSetting.setting == "user_name")
    user_setting = db.execute(query).scalars().first()
    assert json.loads(user_setting.value)["name"] == name

    # delete the user_setting
    db.delete(user_setting)
    db.commit()
    user_setting = db.execute(query).scalars().first()
    assert user_setting is None

    # Check if the User is created
    query = select(User).where(User.id == user_id)
    user = db.execute(query).scalars().first()
    assert user is not None
    assert user.email == email

    # delete the user
    db.delete(user)
    db.commit()
    user = db.execute(query).scalars().first()
    assert db.execute(query).scalars().first() is None


def test_users_edit(db: Session, site_admin_user_token, client, site_admin_user, view_only_user) -> None:
    user_id = view_only_user.id
    email = view_only_user.email
    terms_accepted = view_only_user.termsaccepted
    gpg_key = view_only_user.gpgkey

    name = "test" + str(time())

    headers = {"authorization": site_admin_user_token}
    body = {
        "email": email + "test",
        "name": name + "test",
        "termsaccepted": not terms_accepted,
        "pgpkey": gpg_key + "test",
    }
    response = client.put(f"users/{user_id}", headers=headers, json=body)

    assert response.status_code == 200
    response_json = response.json()
    response_user = response_json.get("user")
    ic(response_user, response_user.get("id"), response_user.get("email"))
    assert response_user.get("id") == str(user_id)
    assert response_user.get("email") == email + "test"
    assert response_user.get("termsaccepted") is not terms_accepted
    assert response_user.get("gpgkey") == gpg_key + "test"
    assert response_user.get("org_id") == str(view_only_user.org_id)
    assert response_json.get("name") == name + "test"


def test_user_view_by_ID(db: Session, site_admin_user_token, client) -> None:
    user_id = db.execute(select(User.id)).scalars().first()
    assert user_id is not None

    headers = {"authorization": site_admin_user_token}
    response = client.get(f"/users/view/{user_id}", headers=headers)

    assert response.status_code == 200
    user = response.json()
    ic(user)

    assert isinstance(user, dict)
    assert "id" in user["User"]
    assert "org_id" in user["User"]
    assert "server_id" in user["User"]
    assert "email" in user["User"]
    assert "autoalert" in user["User"]
    assert "auth_key" in user["User"]
    assert "invited_by" in user["User"]
    assert "gpg_key" in user["User"]
    assert "certif_public" in user["User"]
    assert "nids_sid" in user["User"]
    assert "termsaccepted" in user["User"]
    assert "newsread" in user["User"]
    assert "role_id" in user["User"]
    assert "change_pw" in user["User"]
    assert "contactalert" in user["User"]
    assert "disabled" in user["User"]
    assert "expiration" in user["User"]
    assert "current_login" in user["User"]
    assert "last_login" in user["User"]
    assert "last_api_access" in user["User"]
    assert "force_logout" in user["User"]
    assert "date_created" in user["User"]
    assert "date_modified" in user["User"]
    assert "last_pw_change" in user["User"]
    assert "name" in user["User"]
    assert "totp" in user["User"]
    assert "contact" in user["User"]
    assert "notification" in user["User"]

    assert "id" in user["Role"]
    assert "name" in user["Role"]
    assert "perm_auth" in user["Role"]
    assert "perm_site_admin" in user["Role"]

    assert "id" in user["Organisation"]
    assert "name" in user["Organisation"]

    query = select(UserSetting).where(UserSetting.setting == "user_name" and UserSetting.user_id == user.get("id"))
    user_name = db.execute(query).scalars().one_or_none()
    ic(json.loads(user_name.value)["name"])
    assert user_name is not None
    assert json.loads(user_name.value)["name"] == user["User"].get("name")


def test_users_view_all(db: Session, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/users/view/all", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    for user in response_json:
        assert isinstance(response_json, list)
        assert "id" in user["User"]
        assert "org_id" in user["User"]
        assert "server_id" in user["User"]
        assert "email" in user["User"]
        assert "autoalert" in user["User"]
        assert "auth_key" in user["User"]
        assert "invited_by" in user["User"]
        assert "gpg_key" in user["User"]
        assert "certif_public" in user["User"]
        assert "nids_sid" in user["User"]
        assert "termsaccepted" in user["User"]
        assert "newsread" in user["User"]
        assert "role_id" in user["User"]
        assert "change_pw" in user["User"]
        assert "contactalert" in user["User"]
        assert "disabled" in user["User"]
        assert "expiration" in user["User"]
        assert "current_login" in user["User"]
        assert "last_login" in user["User"]
        assert "last_api_access" in user["User"]
        assert "force_logout" in user["User"]
        assert "date_created" in user["User"]
        assert "date_modified" in user["User"]
        assert "last_pw_change" in user["User"]
        assert "name" in user["User"]
        assert "totp" in user["User"]
        assert "contact" in user["User"]
        assert "notification" in user["User"]

        assert "id" in user["Role"]
        assert "name" in user["Role"]
        assert "perm_auth" in user["Role"]
        assert "perm_site_admin" in user["Role"]

        assert "id" in user["Organisation"]
        assert "name" in user["Organisation"]

        query = select(UserSetting).filter(
            UserSetting.setting == "user_name", UserSetting.user_id == user["User"]["id"]
        )
        user_name = db.execute(query).scalars().one_or_none()
        assert user_name is not None
        assert json.loads(user_name.value)["name"] == user["User"]["name"]

    count = db.query(User).count()
    assert len(response_json) == count


def test_delete_user(site_admin_user_token, site_admin_role, site_admin_user, client, db) -> None:
    email = "test@automated.com" + str(time())
    name = "test_user" + str(time())

    # Creates a new user
    create_response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "authkey": "test",
            "email": email,
            "password": "test",
            "name": name,
            "role": site_admin_role.id,
            "org": site_admin_user.org_id,
            "nids_sid": "12345",
            "disabled": False,
            "contactalert": False,
            "invited_by": site_admin_user.id,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
        },
    )

    # Check if the user was created
    assert create_response.status_code == 200
    created_user = create_response.json()
    user_id = created_user.get("User").get("id")
    assert user_id is not None

    # Check the user and user setting creation
    user_setting_query = select(UserSetting).where(UserSetting.user_id == user_id, UserSetting.setting == "user_name")
    user_setting = db.execute(user_setting_query).scalars().first()
    assert user_setting is not None
    assert json.loads(user_setting.value)["name"] == name

    user_query = select(User).where(User.id == user_id)
    user = db.execute(user_query).scalars().first()
    assert user is not None
    assert user.email == email

    # Api delete call
    delete_response = client.delete(f"/users/{user_id}", headers={"authorization": site_admin_user_token})

    # Shows the error message if the status code is not 200
    if delete_response.status_code != 200:
        print("Error during user deletion:")
        print(delete_response.json())
    assert delete_response.status_code == 200
    db.commit()

    # Check if the user and user setting were deleted from the database
    user_setting = db.execute(user_setting_query).scalars().first()
    assert user_setting is None

    user = db.execute(user_query).scalars().first()
    assert user is None


def test_users_me_unauthorized(client) -> None:
    response = client.get("/users/view/me")
    assert response.status_code == 403


def test_users_create_missing_fields(site_admin_user_token, client) -> None:
    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "authkey": "test",
            "email": "",
            "password": "",
            "name": "",
            "role": "",
            "org": "",
            "nids_sid": "12345",
            "disabled": False,
            "contactalert": False,
            "invited_by": "",
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
        },
    )
    assert response.status_code == 404


def test_users_create_duplicate_email(site_admin_user_token, site_admin_user, site_admin_role, client, db) -> None:
    email = site_admin_user.email
    name = "test_user" + str(time())

    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "authkey": "test",
            "email": email,
            "password": "test",
            "name": name,
            "role": site_admin_role.id,
            "org": site_admin_user.org_id,
            "nids_sid": "12345",
            "disabled": False,
            "contactalert": False,
            "invited_by": site_admin_user.id,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
        },
    )
    assert response.status_code == 406
    assert response.json().get("detail") == "User already exists with this email"


def test_users_edit_unauthorized(client, view_only_user) -> None:
    user_id = view_only_user.id
    email = view_only_user.email

    response = client.put(f"users/{user_id}", json={"email": email + "test"})
    assert response.status_code == 403


def test_user_view_by_invalid_ID(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/users/view/invalid_id", headers=headers)
    assert response.status_code == 404


def test_user_view_non_existent_ID(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/users/view/999999999999", headers=headers)
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_users_delete_non_existent_user(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/users/999999999999", headers=headers)
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_delete_user_token_stub(site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.delete("/users/tokens/1", headers=headers)
    assert response.status_code == 200


def test_get_user_not_found(site_admin_user_token, client, db) -> None:
    user_id = "non_existent_user_id"

    response = client.get(
        f"/users/view/{user_id}",
        headers={"authorization": site_admin_user_token},
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_update_user_not_found(site_admin_user_token, client, db) -> None:
    user_id = "non_existent_user_id"

    response = client.put(
        f"/users/{user_id}",
        headers={"authorization": site_admin_user_token},
        json={"email": "new_email@test.com"}
    )
    assert response.status_code == 404
    assert response.json().get("detail") == "User not found"


def test_update_user_attributes(site_admin_user_token, client, db, view_only_user) -> None:
    user_id = view_only_user.id
    headers = {"authorization": site_admin_user_token}
    body = {
        "authkey": "new_authkey",
        "email": "new_email@test.com",
        "autoalert": True,
        "pgpkey": "new_pgpkey",
        "certif_public": "new_certif_public",
        "termsaccepted": True,
        "change_pw": False,
        "contactalert": True,
        "disabled": False,
        "expiration": "2024-12-31T23:59:59",
        "force_logout": True,
        "external_auth_required": True,
        "external_auth_key": "new_external_auth_key",
        "notification_daily": True,
        "notification_weekly": False,
        "notification_monthly": False,
        "totp": "new_totp",
        "hotp_counter": "5",
        "nids_sid": 54321
    }

    response = client.put(
        f"/users/{user_id}",
        headers=headers,
        json=body
    )
    assert response.status_code == 200
    response_user = response.json().get("user")
    for key, value in body.items():
        if key in response_user:
            assert response_user[key] == value


def test_users_create_no_permission(read_only_user_token, site_admin_user, site_admin_role, client, db) -> None:
    email = "test@automated.com" + str(time())
    name = "test_user" + str(time())

    response = client.post(
        "/users",
        headers={"authorization": read_only_user_token},
        json={
            "authkey": "test",
            "email": email,
            "password": "test",
            "name": name,
            "role": site_admin_role.id,
            "org": site_admin_user.org_id,
            "nids_sid": "12345",
            "disabled": False,
            "contactalert": False,
            "invited_by": site_admin_user.id,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
        },
    )

    assert response.status_code == 401


def test_users_edit_no_permission(db: Session, read_only_user_token, client, site_admin_user, view_only_user) -> None:
    user_id = view_only_user.id
    email = view_only_user.email
    terms_accepted = view_only_user.termsaccepted
    gpg_key = view_only_user.gpgkey

    name = "test" + str(time())

    headers = {"authorization": read_only_user_token}
    body = {
        "email": email + "test",
        "name": name + "test",
        "termsaccepted": not terms_accepted,
        "pgpkey": gpg_key + "test",
    }
    response = client.put(f"users/{user_id}", headers=headers, json=body)

    assert response.status_code == 401


def test_user_view_by_ID_no_permission(db: Session, read_only_user_token, client) -> None:
    headers = {"authorization": read_only_user_token}
    response = client.get(f"/users/view/{2}", headers=headers)

    assert response.status_code == 401


def test_users_view_all_unauthorized(db: Session, read_only_user_token, client) -> None:
    headers = {"authorization": read_only_user_token}
    response = client.get("/users/view/all", headers=headers)

    assert response.status_code == 401
