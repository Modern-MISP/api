from time import time
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from mmisp.api.auth import decode_exchange_token, encode_exchange_token, encode_token
from mmisp.api_schemas.authentication.exchange_token_login_body import ExchangeTokenLoginBody
from mmisp.api_schemas.authentication.password_login_body import PasswordLoginBody
from mmisp.api_schemas.authentication.start_login_body import StartLoginBody
from mmisp.api_schemas.authentication.start_login_response import LoginType, StartLoginResponse
from mmisp.api_schemas.authentication.token_response import TokenResponse
from mmisp.config import config
from mmisp.db.database import get_db, with_session_management
from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.db.models.user import User
from mmisp.util.crypto import verify_password

router = APIRouter(tags=["authentication"])


@router.post("/auth/login/start", response_model=StartLoginResponse)
@with_session_management
async def start_login(db: Annotated[Session, Depends(get_db)], body: StartLoginBody) -> dict:
    user: User | None = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    identity_providers: list[OIDCIdentityProvider] = (
        db.query(OIDCIdentityProvider)
        .filter(OIDCIdentityProvider.active.is_(True), OIDCIdentityProvider.org_id == user.org_id)
        .all()
    )

    login_type = LoginType.PASSWORD

    if user.external_auth_required:
        login_type = LoginType.IDENTITY_PROVIDER

    return {"loginType": login_type, "identityProviders": identity_providers}


@router.post("/auth/login/password")
@with_session_management
async def password_login(db: Annotated[Session, Depends(get_db)], body: PasswordLoginBody) -> TokenResponse:
    user: User | None = db.query(User).filter(User.email == body.email).first()

    if not user or user.external_auth_required or not verify_password(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return TokenResponse(token=encode_token(str(user.id)))


@router.get("/auth/login/idp/{identityProviderId}/authorize", response_class=RedirectResponse)
@with_session_management
async def redirect_to_idp(
    db: Annotated[Session, Depends(get_db)], identity_provider_id: Annotated[int, Path(alias="identityProviderId")]
) -> RedirectResponse:
    identity_provider: OIDCIdentityProvider | None = db.get(OIDCIdentityProvider, identity_provider_id)

    if (not identity_provider) or (not identity_provider.active):
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    oidc_config = await _get_oidc_config(identity_provider.base_url)

    query_params = {
        "scope": "openid profile email",
        "response_type": "code",
        "client_id": identity_provider.client_id,
        "redirect_uri": f"{config.OWN_URL}/auth/login/idp/{identity_provider.id}/callback",
    }

    authorization_endpoint = oidc_config["authorization_endpoint"]

    url = f"{authorization_endpoint}?{urlencode(query_params)}"

    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse)
@router.post("/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse)
@with_session_management
async def redirect_to_frontend(
    db: Annotated[Session, Depends(get_db)],
    identity_provider_id: Annotated[int, Path(alias="identityProviderId")],
    code: str,
) -> RedirectResponse:
    identity_provider: OIDCIdentityProvider | None = db.get(OIDCIdentityProvider, identity_provider_id)

    if not identity_provider or not identity_provider.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    oidc_config = await _get_oidc_config(identity_provider.base_url)
    token_endpoint = oidc_config["token_endpoint"]

    body_params = {
        "grant_type": "authorization_code",
        "scope": "openid profile email",
        "client_secret": identity_provider.client_secret,
        "client_id": identity_provider.client_id,
        "redirect_uri": f"{config.OWN_URL}/auth/login/idp/{identity_provider.id}/callback",
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_endpoint,
            content=urlencode(body_params),
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

    access_token: str = token_response.json().get("access_token", None)

    if not access_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user_info_endpoint: str = oidc_config["userinfo_endpoint"]

    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            user_info_endpoint,
            headers={"authorization": f"Bearer {access_token}"},
        )

    user_info: dict = user_info_response.json()

    if not user_info.get("email", None) or not user_info.get("sub", None):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user: User | None = db.query(User).filter(User.email == user_info["email"]).first()

    if (
        not user
        or user.org_id != identity_provider.org_id
        or user.disabled
        or (user.sub and user.sub != user_info["sub"])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if not user.sub:
        user.sub = user_info["sub"]
        user.date_modified = time()
        db.commit()

    exchange_token = encode_exchange_token(str(user.id))

    return RedirectResponse(
        url=f"{config.DASHBOARD_URL}?exchangeToken={exchange_token}", status_code=status.HTTP_302_FOUND
    )


@router.post("/auth/login/token")
async def exchange_token_login(body: ExchangeTokenLoginBody) -> TokenResponse:
    user_id = decode_exchange_token(body.exchangeToken)

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return TokenResponse(token=encode_token(user_id))


async def _get_oidc_config(base_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        oidc_config_response = await client.get(f"{base_url}/.well-known/openid-configuration")

    return oidc_config_response.json()
