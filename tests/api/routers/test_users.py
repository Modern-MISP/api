import json
from time import time

from icecream import ic
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.db.models.user import User
from mmisp.db.models.user_setting import UserSetting


def test_users_me(site_admin_user_token, site_admin_user, client) -> None:
    response = client.get("/users/view/me", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == str(site_admin_user.id)


def test_users_create(site_admin_user_token, site_admin_user, client, db) -> None:
    email = "test@automated.com" + str(time())
    name = "test_user" + str(time())

    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "email": email,
            "password": "test",
            "name": name,
            "role_id": 0,
            "org_id": site_admin_user.org_id,
            "nids_sid": "12345",
            "disabled": False,
            "contact_enabled": False,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
            "gpgkey": "Test",
        },
    )

    # Check if the Status Code is 200
    json_str = response.json()
    assert response.status_code == 200

    # Check if the User_setting user_name is created
    query = select(UserSetting).where(UserSetting.user_id == json_str.get("id") and UserSetting.setting == "user_name")
    user_setting = db.execute(query).scalars().first()
    assert json.loads(user_setting.value)["name"] == name

    # delete the user_setting
    db.delete(user_setting)
    db.commit()
    user_setting = db.execute(query).scalars().first()
    assert user_setting is None

    # Check if the User is created
    query = select(User).where(User.id == json_str.get("id"))
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

    name = (
        db.execute(select(UserSetting).where(UserSetting.setting == "user_name" and UserSetting.user_id == user_id))
        .scalars()
        .first()
        .value
    )

    headers = {"authorization": site_admin_user_token}
    body = {
        "email": email + "test",
        "name": name + "test",
        "termsaccepted": not terms_accepted,
        "gpgkey": gpg_key + "test",
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


def test_users_view_all(db: Session, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/users/view/all", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    assert isinstance(response_json, list)
    response_json = response.json()
    for user in response_json:
        assert isinstance(response_json, list)
        assert "id" in user
        assert "organisation" in user
        assert "role" in user
        assert "nids" in user
        assert "name" in user
        assert "email" in user
        assert "last_login" in user
        assert "created" in user
        assert "totp" in user
        assert "contact" in user
        assert "notification" in user
        assert "gpg_key" in user
        assert "terms" in user

        query = select(UserSetting).where(UserSetting.setting == "user_name" and UserSetting.user_id == user.get("id"))
        user_name = db.execute(query).scalars().first()
        assert user_name is not None
        assert json.loads(user_name.value)["name"] == user.get("name")

"""
def test_delete_user(db: Session, site_admin_user_token, client) -> None:
    email = "test_delete@automated.com"
    name = "test_delete_user"
    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "email": email,
            "password": "test",
            "name": name,
            "role_id": 0,
            "org_id": 1,
            "nids_sid": "12345",
            "disabled": False,
            "contact_enabled": False,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
            "gpgkey": "Test",
        },
    )
    json = response.json()
    assert response.status_code == 200

    user_id = json.get("id")

    # Check if user exists
    query = select(User).where(User.id == user_id)
    user = db.execute(query).scalars().first()
    assert user is not None

    # Delete user
    response = client.delete(f"/users/{user_id}", headers={"authorization": site_admin_user_token})
    json = response.json()
    assert response.status_code == 200
    assert json.get("success") is True
    assert json.get("id") == user_id

    # Test if user is deleted
    user = db.execute(query).scalars().first()
    assert user is None
"""
