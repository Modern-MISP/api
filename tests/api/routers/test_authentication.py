from time import time_ns

import pytest
import respx
from fastapi import status
from httpx import Response

from mmisp.api.auth import _decode_token, encode_exchange_token, encode_token
from mmisp.api.config import config
from mmisp.api_schemas.authentication.start_login_response import LoginType
from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.db.models.user import User
from mmisp.util.crypto import hash_secret
from mmisp.util.uuid import uuid
from tests.database import get_db
from tests.environment import client, environment
from tests.generators.model_generators.identity_provider_generator import generate_oidc_identity_provider
from tests.generators.model_generators.user_generator import generate_user


class AuthEnvironment:
    def __init__(
        self: "AuthEnvironment",
        password: str,
        password_auth_user: User,
        external_auth_user: User,
        identity_provider: OIDCIdentityProvider,
        well_known_oidc_config: dict,
    ) -> None:
        self.password = password
        self.password_auth_user = password_auth_user
        self.external_auth_user = external_auth_user
        self.identity_provider = identity_provider
        self.well_known_oidc_config = well_known_oidc_config


@pytest.fixture(scope="module")
def auth_environment() -> AuthEnvironment:
    db = get_db()
    password = uuid()
    hashed_password = hash_secret(password)

    password_auth_user = generate_user()
    password_auth_user.org_id = environment.instance_owner_org.id
    password_auth_user.role_id = environment.org_admin_role.id
    password_auth_user.server_id = 0
    password_auth_user.password = hashed_password

    external_auth_user = generate_user()
    external_auth_user.org_id = environment.instance_owner_org.id
    external_auth_user.role_id = environment.org_admin_role.id
    external_auth_user.server_id = 0
    external_auth_user.password = hashed_password
    external_auth_user.sub = f"test-idp|{uuid()}-{time_ns()}"
    external_auth_user.external_auth_required = True

    identity_provider = generate_oidc_identity_provider()
    identity_provider.org_id = environment.instance_owner_org.id

    db.add_all([password_auth_user, external_auth_user, identity_provider])
    db.commit()

    db.refresh(password_auth_user)
    db.refresh(external_auth_user)
    db.refresh(identity_provider)
    db.close()

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


class TestStartLogin:
    @staticmethod
    def test_start_login_password() -> None:
        user = environment.instance_owner_org_admin_user

        response = client.post("/auth/login/start", json={"email": user.email})

        assert response.status_code == status.HTTP_200_OK
        json: dict = response.json()

        assert json["loginType"] == LoginType.PASSWORD.value
        assert json["identityProviders"] == []

    @staticmethod
    def test_start_login_idp(auth_environment: AuthEnvironment) -> None:
        response = client.post("/auth/login/start", json={"email": auth_environment.external_auth_user.email})

        assert response.status_code == status.HTTP_200_OK
        json: dict = response.json()

        assert json["loginType"] == LoginType.IDENTITY_PROVIDER.value
        assert json["identityProviders"][0]["id"] == str(auth_environment.identity_provider.id)
        assert json["identityProviders"][0]["name"] == auth_environment.identity_provider.name

    @staticmethod
    def test_start_login_unknown() -> None:
        response = client.post("/auth/login/start", json={"email": f"doesnotexist{time_ns()}@test.com"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPasswordLogin:
    @staticmethod
    def test_password_login_correct(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/password",
            json={"email": auth_environment.password_auth_user.email, "password": auth_environment.password},
        )

        assert response.status_code == status.HTTP_200_OK
        json: dict = response.json()

        user_id = _decode_token(json["token"])
        assert user_id == auth_environment.password_auth_user.id

    @staticmethod
    def test_password_login_wrong_email(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/password",
            json={"email": f"random{time_ns()}@random.com", "password": auth_environment.password},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @staticmethod
    def test_password_login_wrong_password(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/password",
            json={
                "email": auth_environment.password_auth_user.email,
                "password": auth_environment.password_auth_user.password,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @staticmethod
    def test_password_login_idp_user(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/password",
            json={"email": auth_environment.external_auth_user.email, "password": auth_environment.password},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRedirectToIDP:
    @staticmethod
    @respx.mock
    def test_redirect_to_idp_correct(auth_environment: AuthEnvironment) -> None:
        route = respx.get(f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration").mock(
            return_value=Response(200, json=auth_environment.well_known_oidc_config)
        )

        response = client.get(
            f"/auth/login/idp/{auth_environment.identity_provider.id}/authorize", follow_redirects=False
        )

        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"].startswith(
            auth_environment.well_known_oidc_config["authorization_endpoint"]
        )
        assert route.called

    @staticmethod
    def test_redirect_to_idp_not_existing() -> None:
        response = client.get("/auth/login/idp/-1/authorize")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRedirectToFrontend:
    @staticmethod
    @respx.mock
    def test_redirect_to_frontend_correct(auth_environment: AuthEnvironment) -> None:
        config_route = respx.get(
            f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration"
        ).mock(return_value=Response(200, json=auth_environment.well_known_oidc_config))
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

    @staticmethod
    def test_redirect_to_frontend_idp_does_not_exist() -> None:
        response = client.get("/auth/login/idp/-1/callback?code=test-code")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @staticmethod
    @respx.mock
    def test_redirect_to_frontend_no_access_token(auth_environment: AuthEnvironment) -> None:
        config_route = respx.get(
            f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration"
        ).mock(return_value=Response(200, json=auth_environment.well_known_oidc_config))
        token_route = respx.post(auth_environment.well_known_oidc_config["token_endpoint"]).mock(
            return_value=Response(200, json={})
        )

        response = client.get(f"/auth/login/idp/{auth_environment.identity_provider.id}/callback?code=test-code")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert config_route.called
        assert token_route.called

    @staticmethod
    @respx.mock
    def test_redirect_to_frontend_invalid_sub(auth_environment: AuthEnvironment) -> None:
        config_route = respx.get(
            f"{auth_environment.identity_provider.base_url}/.well-known/openid-configuration"
        ).mock(return_value=Response(200, json=auth_environment.well_known_oidc_config))
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


class TestExchangeTokenLogin:
    @staticmethod
    def test_exchange_token_login_valid(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/token",
            json={"exchangeToken": encode_exchange_token(str(auth_environment.external_auth_user.id))},
        )

        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert _decode_token(json["token"]) == auth_environment.external_auth_user.id

    @staticmethod
    def test_exchange_token_login_regular_token(auth_environment: AuthEnvironment) -> None:
        response = client.post(
            "/auth/login/token",
            json={"exchangeToken": encode_token(str(auth_environment.external_auth_user.id))},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
