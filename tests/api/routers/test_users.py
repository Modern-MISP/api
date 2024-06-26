from icecream import ic
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from mmisp.db.models.user import User


def test_users_me(site_admin_user_token, site_admin_user, client) -> None:
    response = client.get("/users/view/me", headers={"authorization": site_admin_user_token})

    assert response.status_code == 200
    json = response.json()
    assert json.get("User").get("id") == str(site_admin_user.id)


def test_users_create(site_admin_user_token, site_admin_user, client, db) -> None:
    email = "test@automated.com"
    response = client.post(
        "/users",
        headers={"authorization": site_admin_user_token},
        json={
            "email": email,
            "password": "test",
            "name": "test",
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

    json = response.json()
    assert response.status_code == 200

    query = select(User).where(User.id == json.get("id"))
    user = db.execute(query).scalars().first()
    assert user is not None
    assert user.email == email

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
