from collections.abc import Sequence
from time import time
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select

from mmisp.api.auth import decode_exchange_token, encode_exchange_token, encode_token
from mmisp.api.config import config
from mmisp.api_schemas.authentication import (
    ExchangeTokenLoginBody,
    LoginType,
    PasswordLoginBody,
    StartLoginBody,
    StartLoginResponse,
    TokenResponse,
    ChangePasswordBody,
    ChangePasswordResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.db.models.user import User
from mmisp.util.crypto import verify_secret

router = APIRouter(tags=["authentication"])


@router.post("/auth/openID/setOpenIDProvider")
async def set_openID_provider(db: Annotated[Session, Depends(get_db)]):
    """Sets a new OpenID provider

    Input:

    -database

    Output:

    -openid provider
    """
    return None


@router.delete(
    "/auth/openID/delete/{openIDProvider}",
    summary="Deletes an OpenID Provider by its ID",
)
async def delete_openID_provider(TODO):
    """Deletes an OpenID provider

    Input:

    -openid provider

    Output:

    -database
    """
    return await _delete_openID_provider(db, openIDProvider)


@router.post("/auth/login/start", response_model=StartLoginResponse)
async def start_login(db: Annotated[Session, Depends(get_db)], body: StartLoginBody) -> dict:
    """Starts the login process.

    Input:

    -the database

    -the request body

    Output:

    -dict
    """
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(OIDCIdentityProvider).filter(
            OIDCIdentityProvider.active.is_(True), OIDCIdentityProvider.org_id == user.org_id
        )
    )
    identity_providers: Sequence[OIDCIdentityProvider] = result.scalars().all()

    login_type = LoginType.PASSWORD

    if user.external_auth_required:
        login_type = LoginType.IDENTITY_PROVIDER

    return {"loginType": login_type, "identityProviders": identity_providers}


@router.post("/auth/login/password")
async def password_login(db: Annotated[Session, Depends(get_db)], body: PasswordLoginBody) -> TokenResponse:
    """Login with password.

    Input:

    -the database

    -the request body

    Output:

    -the login token
    """
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()

    if not user or user.external_auth_required or not verify_secret(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return TokenResponse(token=encode_token(str(user.id)), reqiuredPasswordChange=False)


@router.post("/auth/login/setOwnPassword")
async def reset_password(db: Annotated[Session, Depends(get_db)]):
    """Resets password

    Input:

    -the database

    Output:

    -the response form the api from resetting the user's password
    """
    return None


@router.get(
    "/auth/login/idp/{identityProviderId}/authorize", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND
)
async def redirect_to_idp(
    db: Annotated[Session, Depends(get_db)], identity_provider_id: Annotated[int, Path(alias="identityProviderId")]
) -> RedirectResponse:
    """Redirects to Idp.

    Input:

    -the database

    -the identity provider id

    Output:
    -the redirection
    """
    identity_provider: OIDCIdentityProvider | None = await db.get(OIDCIdentityProvider, identity_provider_id)

    if not identity_provider or not identity_provider.active:
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


@router.get(
    "/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND
)
@router.post(
    "/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND
)
async def redirect_to_frontend(
    db: Annotated[Session, Depends(get_db)],
    identity_provider_id: Annotated[int, Path(alias="identityProviderId")],
    code: str,
) -> RedirectResponse:
    """Redirects to the frontend.

    Input:

    -the database

    -the identity provider id

    -the code

    Output:

    -the redirection
    """
    identity_provider: OIDCIdentityProvider | None = await db.get(OIDCIdentityProvider, identity_provider_id)

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

    result = await db.execute(select(User).filter(User.email == user_info["email"]))
    user: User | None = result.scalars().first()

    if (
        not user
        or user.org_id != identity_provider.org_id
        or user.disabled
        or (user.sub and user.sub != user_info["sub"])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if not user.sub:
        user.sub = user_info["sub"]
        user.date_modified = int(time())
        await db.commit()

    exchange_token = encode_exchange_token(str(user.id))

    return RedirectResponse(
        url=f"{config.DASHBOARD_URL}?exchangeToken={exchange_token}", status_code=status.HTTP_302_FOUND
    )


@router.post("/auth/login/token")
async def exchange_token_login(body: ExchangeTokenLoginBody) -> TokenResponse:
    """Login with exchange token.

    Inout:

    -the request body

    Output:

    -the login token
    """
    user_id = decode_exchange_token(body.exchangeToken)

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return TokenResponse(token=encode_token(str(user_id)), reqiuredPasswordChange=False)


@router.put("/auth/setPassword/{userId}")
async def change_password(body: ChangePasswordBody) -> ChangePasswordResponse:
    """Changes the password of the user.

    Input:

    -the request body

    Output:

    -the response from the api after the password change request
    """
    # ToDo
    return ChangePasswordResponse(successful=True)  # Set to True to pass the pipeline


async def _get_oidc_config(base_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        oidc_config_response = await client.get(f"{base_url}/.well-known/openid-configuration")

    return oidc_config_response.json()


# --- endpoint logic ---


async def _delete_openID_provider(db: Session, openIDProvider: str):
    return None
