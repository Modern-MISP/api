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
    email = "test@automated.com"
    name = "test_user"

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
            "totp": None,
            "contact_enabled": False,
            "notification_daily": False,
            "notification_weekly": True,
            "notification_monthly": True,
            "termsaccepted": False,
            "gpgkey": "Test",
        },
    )

    # Check if the Status Code is 200
    json = response.json()
    assert response.status_code == 200

    # Check if the User_setting user_name is created
    query = select(UserSetting).where(UserSetting.user_id == json.get("id") and UserSetting.setting == "user_name")
    user_setting = db.execute(query).scalars().first()
    assert user_setting.value == name

    # delete the user_setting
    db.delete(user_setting)
    db.commit()
    user_setting = db.execute(query).scalars().first()
    assert user_setting is None

    # Check if the User is created
    query = select(User).where(User.id == json.get("id"))
    user = db.execute(query).scalars().first()
    assert user is not None
    assert user.email == email

    # delete the user
    db.delete(user)
    db.commit()
    user = db.execute(query).scalars().first()
    assert db.execute(query).scalars().first() is None


def test_users_view_all(db: Session, site_admin_user_token, client) -> None:
    headers = {"authorization": site_admin_user_token}
    response = client.get("/users/view/all", headers=headers)

    assert response.status_code == 200
    response_json = response.json()
    ic(type(response_json))
    ic(isinstance(response_json, dict))
    assert isinstance(response_json, dict)
