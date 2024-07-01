from dataclasses import dataclass
from time import time_ns

import pytest
import respx
from fastapi import status
from httpx import Response
from icecream import ic
from sqlalchemy.orm import Session

from mmisp.api.auth import _decode_token, encode_exchange_token, encode_token
from mmisp.api.config import config
from mmisp.api_schemas.authentication import LoginType
from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret, verify_secret
from mmisp.util.uuid import uuid
from tests.generators.model_generators.identity_provider_generator import generate_oidc_identity_provider
from tests.generators.model_generators.user_generator import generate_user


@dataclass
class AuthEnvironment:
    password: str
    password_auth_user: User
    external_auth_user: User
    identity_provider: OIDCIdentityProvider
    well_known_oidc_config: dict


@pytest.fixture
def password():
    return uuid()


@pytest.fixture
def password_auth_user(db, password, instance_owner_org, org_admin_role):
    hashed_password = hash_secret(password)

    user = generate_user()
    user.org_id = instance_owner_org.id
    user.role_id = org_admin_role.id
    user.server_id = 0
    user.password = hashed_password

    db.add(user)
    db.commit()

    yield user

    db.delete(user)
    db.commit()


@pytest.fixture
def external_auth_user(db, password, instance_owner_org, org_admin_role):
    hashed_password = hash_secret(password)

    user = generate_user()
    user.org_id = instance_owner_org.id
    user.role_id = org_admin_role.id
    user.server_id = 0
    user.password = hashed_password
    user.sub = f"test-idp|{uuid()}-{time_ns()}"
    user.external_auth_required = True

    db.add(user)
    db.commit()

    yield user

    db.delete(user)
    db.commit()


@pytest.fixture
def identity_provider(db, instance_owner_org):
    identity_provider = generate_oidc_identity_provider()
    identity_provider.org_id = instance_owner_org.id

    db.add(identity_provider)
    db.commit()

    yield identity_provider

    db.delete(identity_provider)
    db.commit()


@pytest.fixture
def auth_environment(password, password_auth_user, external_auth_user, identity_provider) -> AuthEnvironment:
    well_known_oidc_config = {
        "authorization_endpoint": f"{identity_provider.base_url}/authorize",
        "token_endpoint": f"{identity_provider.base_url}/oauth/token",
        "userinfo_endpoint": f"{identity_provider.base_url}/userinfo",
    }

    return AuthEnvironment(
        password=password,
        password_auth_user=password_auth_user,
        external_auth_user=external_auth_user,
        identity_provider=identity_provider,
        well_known_oidc_config=well_known_oidc_config,
    )


def test_start_login_password(instance_owner_org_admin_user, client) -> None:
    user = instance_owner_org_admin_user

    response = client.post("/auth/login/start", json={"email": user.email})

    assert response.status_code == status.HTTP_200_OK
    json: dict = response.json()

    assert json["loginType"] == LoginType.PASSWORD.value
    assert json["identityProviders"] == []


def test_start_login_idp(auth_environment: AuthEnvironment, client) -> None:
    response = client.post("/auth/login/start", json={"email": auth_environment.external_auth_user.email})

    assert response.status_code == status.HTTP_200_OK
    json: dict = response.json()

    assert json["loginType"] == LoginType.IDENTITY_PROVIDER.value
    assert json["identityProviders"][0]["id"] == str(auth_environment.identity_provider.id)
    assert json["identityProviders"][0]["name"] == auth_environment.identity_provider.name


def test_start_login_unknown(client) -> None:
    response = client.post("/auth/login/start", json={"email": f"doesnotexist{time_ns()}@test.com"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_password_login_correct(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/password",
        json={"email": auth_environment.password_auth_user.email, "password": auth_environment.password},
    )

    assert response.status_code == status.HTTP_200_OK
    json: dict = response.json()

    user_id = _decode_token(json["token"])
    assert user_id == auth_environment.password_auth_user.id


def test_password_login_wrong_email(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/password",
        json={"email": f"random{time_ns()}@random.com", "password": auth_environment.password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_password_login_wrong_password(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/password",
        json={
            "email": auth_environment.password_auth_user.email,
            "password": auth_environment.password_auth_user.password,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_password_login_idp_user(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/password",
        json={"email": auth_environment.external_auth_user.email, "password": auth_environment.password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@respx.mock
def test_redirect_to_idp_correct(auth_environment: AuthEnvironment, client) -> None:
    route = respx.get(f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration").mock(
        return_value=Response(200, json=auth_environment.well_known_oidc_config)
    )

    response = client.get(f"/auth/login/idp/{auth_environment.identity_provider.id}/authorize", follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"].startswith(auth_environment.well_known_oidc_config["authorization_endpoint"])
    assert route.called


def test_redirect_to_idp_not_existing(client) -> None:
    response = client.get("/auth/login/idp/-1/authorize")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@respx.mock
def test_redirect_to_frontend_correct(auth_environment: AuthEnvironment, client) -> None:
    config_route = respx.get(f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration").mock(
        return_value=Response(200, json=auth_environment.well_known_oidc_config)
    )
    token_route = respx.post(auth_environment.well_known_oidc_config["token_endpoint"]).mock(
        return_value=Response(200, json={"access_token": "test-token"})
    )
    info_route = respx.get(auth_environment.well_known_oidc_config["userinfo_endpoint"]).mock(
        return_value=Response(
            200,
            json={
                "sub": auth_environment.external_auth_user.sub,
                "email": auth_environment.external_auth_user.email,
            },
        )
    )

    response = client.get(
        f"/auth/login/idp/{auth_environment.identity_provider.id}/callback?code=test-code", follow_redirects=False
    )

    assert response.status_code == status.HTTP_302_FOUND

    location = response.headers["location"]

    assert location.startswith(config.DASHBOARD_URL)
    assert config_route.called
    assert token_route.called
    assert info_route.called


def test_redirect_to_frontend_idp_does_not_exist(client) -> None:
    response = client.get("/auth/login/idp/-1/callback?code=test-code")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@respx.mock
def test_redirect_to_frontend_no_access_token(auth_environment: AuthEnvironment, client) -> None:
    config_route = respx.get(f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration").mock(
        return_value=Response(200, json=auth_environment.well_known_oidc_config)
    )
    token_route = respx.post(auth_environment.well_known_oidc_config["token_endpoint"]).mock(
        return_value=Response(200, json={})
    )

    response = client.get(f"/auth/login/idp/{auth_environment.identity_provider.id}/callback?code=test-code")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert config_route.called
    assert token_route.called


@respx.mock
def test_redirect_to_frontend_invalid_sub(auth_environment: AuthEnvironment, client) -> None:
    config_route = respx.get(f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration").mock(
        return_value=Response(200, json=auth_environment.well_known_oidc_config)
    )
    token_route = respx.post(auth_environment.well_known_oidc_config["token_endpoint"]).mock(
        return_value=Response(200, json={"access_token": "test-token"})
    )
    info_route = respx.get(auth_environment.well_known_oidc_config["userinfo_endpoint"]).mock(
        return_value=Response(
            200,
            json={
                "sub": f"invalid-sub{time_ns()}",
                "email": auth_environment.external_auth_user.email,
            },
        )
    )

    response = client.get(f"/auth/login/idp/{auth_environment.identity_provider.id}/callback?code=test-code")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert config_route.called
    assert token_route.called
    assert info_route.called


def test_exchange_token_login_valid(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/token",
        json={"exchangeToken": encode_exchange_token(str(auth_environment.external_auth_user.id))},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert _decode_token(json["token"]) == auth_environment.external_auth_user.id


def test_exchange_token_login_regular_token(auth_environment: AuthEnvironment, client) -> None:
    response = client.post(
        "/auth/login/token",
        json={"exchangeToken": encode_token(str(auth_environment.external_auth_user.id))},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_change_password_userID(db: Session, site_admin_user_token, client, view_only_user) -> None:
    newPassword = "TEST"

    response = client.put(
        "/auth/setPassword/%s" % view_only_user.id,
        headers={"authorization": site_admin_user_token},
        json={"password": newPassword},
    )
    db.refresh(view_only_user)

    print(newPassword)
    ic(response.json())
    assert response.status_code == 200
    assert response.json() == {"successful": True}
    assert verify_secret(newPassword, view_only_user.password)


def test_openid_edit_provider(db: Session, site_admin_user_token, client, auth_environment: AuthEnvironment) -> None:
    response = client.post(
        f"/auth/openID/editOpenIDConnectProvider/{auth_environment.identity_provider.id}",
        headers={"authorization": site_admin_user_token},
        json={
            "name": "Test",
            "org_id": 1,
            "active": True,
            "base_url": "http://test.com",
            "client_id": "test",
            "client_secret": "test",
        },
    )
    db.refresh(auth_environment.identity_provider)

    assert response.status_code == 200
    assert response.json() == {"successful": True}
    assert auth_environment.identity_provider.name == "Test"
    assert auth_environment.identity_provider.org_id == 1
    assert auth_environment.identity_provider.active is True
    assert auth_environment.identity_provider.base_url == "http://test.com"
    assert auth_environment.identity_provider.client_id == "test"
    assert auth_environment.identity_provider.client_secret == "test"


def test_openid_delete_provider(db: Session, site_admin_user_token, client, auth_environment: AuthEnvironment) -> None:
    response = client.delete(
        f"/auth/openID/delete/{auth_environment.identity_provider.id}",
        headers={"authorization": site_admin_user_token},
    )

    assert response.status_code == 200
    assert response.json() == {"successful": True}
    assert (
        db.query(OIDCIdentityProvider).where(OIDCIdentityProvider.id == auth_environment.identity_provider.id).first()
        is None
    )
