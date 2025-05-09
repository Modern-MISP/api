import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import (
    Auth,
    AuthStrategy,
    Permission,
    authorize,
    check_permissions,
    decode_exchange_token,
    encode_token,
)
from mmisp.api_schemas.authentication import (
    ChangeLoginInfoResponse,
    ChangePasswordBody,
    ExchangeTokenLoginBody,
    GetIdentityProviderResponse,
    IdentityProviderBody,
    IdentityProviderCallbackBody,
    IdentityProviderEditBody,
    IdentityProviderInfo,
    LoginType,
    PasswordLoginBody,
    SetPasswordBody,
    StartLoginBody,
    StartLoginResponse,
    TokenResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.db.models.user import User
from mmisp.lib.logger import alog
from mmisp.util.crypto import hash_secret, verify_secret

router = APIRouter(tags=["authentication"])

logger = logging.getLogger("mmisp")


@router.get("/auth/openID/getAllOpenIDConnectProvidersInfo")
@alog
async def get_all_open_id_connect_providers_info(
    db: Annotated[Session, Depends(get_db)],
) -> list[IdentityProviderInfo]:
    """
    Fetches all OpenID Connect providers

    args:
    - Authorization token
    - Database session

    returns:
    - List of OpenID Connect providers
    """
    return await _get_all_open_id_connect_providers_info(db)


@router.get("/auth/openID/getAllOpenIDConnectProviders")
@alog
async def get_all_open_id_connect_providers(
    db: Annotated[Session, Depends(get_db)],
) -> list[GetIdentityProviderResponse]:
    """
    Fetches all OpenID Connect providers

    args:
    - Authorization token
    - Database session

    returns:
    - List of OpenID Connect providers
    """
    return await _get_all_open_id_connect_providers(db)


@router.get("/auth/openID/getOpenIDConnectProvider/{providerId}")
@alog
async def get_open_id_connect_provider_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    provider_id: Annotated[str, Path(alias="providerId")],
) -> GetIdentityProviderResponse:
    """
    Fetches a single OpenID Connect provider by its ID

    args:
    - Authorization token
    - Database session
    - Provider ID

    returns:
    - OpenID Connect provider details
    """
    return await _get_open_id_connect_provider_by_id(auth, db, provider_id)


@router.post("/auth/openID/addOpenIDConnectProvider")
@alog
async def add_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: IdentityProviderBody,
) -> IdentityProviderInfo:
    """Adds a new OpenID Connect provider

    args:

    - database

    returns:

    - openID Connect provider
    """
    return await _add_openID_Connect_provider(auth, db, body)


@router.post("/auth/openID/editOpenIDConnectProvider/{openIDConnectProvider}")
@alog
async def edit_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    open_Id_Connect_provider_Id: Annotated[str, Path(alias="openIDConnectProvider")],
    body: IdentityProviderEditBody,
) -> ChangeLoginInfoResponse:
    """Edits an OpenID Connect provider

    args:

    - OpenID Connect provider

    - The current database

    returns:

    - updated OpenID Connect provider
    """
    return await _edit_openID_Connect_provider(auth, db, open_Id_Connect_provider_Id, body)


@router.delete(
    "/auth/openID/delete/{openIDConnectProvider}",
    summary="Deletes an OpenID Connect Provider by its ID",
)
@alog
async def delete_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    open_Id_Connect_provider_Id: Annotated[str, Path(alias="openIDConnectProvider")],
) -> ChangeLoginInfoResponse:
    """Deletes an OpenID Connect provider

    args:

    - OpenID Connect provider

    - The current database

    returns:

    - database
    """
    return await _delete_openID_Connect_provider(db, open_Id_Connect_provider_Id)


@router.post("/auth/login/start", response_model=StartLoginResponse)
@alog
async def start_login(db: Annotated[Session, Depends(get_db)], body: StartLoginBody) -> dict:
    """Starts the login process.

    args:

    - the database

    - the request body

    returns:

    - dict
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
@alog
async def password_login(db: Annotated[Session, Depends(get_db)], body: PasswordLoginBody) -> TokenResponse:
    """Login with password.

    args:

    - the database

    - the request body

    returns:

    - the login token
    """
    return await _password_login(db, body)


@router.post(
    "/auth/login/setOwnPassword",
    summary="User sets their password to a new password",
)
@alog
async def set_password(
    db: Annotated[Session, Depends(get_db)],
    body: ChangePasswordBody,
) -> TokenResponse:
    """Sets the password of the user to a new password.

    args:

    - the database

    returns:

    - the response form the api after the password change request
    """
    return await _set_own_password(db, body)


@router.get("/auth/login/idp/{identityProviderName}/callback")
@router.post("/auth/login/idp/{identityProviderName}/callback")
@alog
async def redirect_to_frontend(
    db: Annotated[Session, Depends(get_db)],
    identity_provider_name: Annotated[str, Path(alias="identityProviderName")],
    body: IdentityProviderCallbackBody,
) -> TokenResponse:
    """Redirects to the frontend.

    args:

    - the database

    - the identity provider id

    - the code

    returns:

    - the redirection
    """
    identity_provider_result = await db.execute(
        select(OIDCIdentityProvider).where(OIDCIdentityProvider.name == identity_provider_name)
    )
    identity_provider: OIDCIdentityProvider | None = identity_provider_result.scalars().one_or_none()

    if not identity_provider or not identity_provider.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    oidc_config = await _get_oidc_config(identity_provider.base_url)
    token_endpoint = oidc_config["token_endpoint"]

    body_params = {
        "grant_type": "authorization_code",
        "scope": "openid profile email",
        "client_id": identity_provider.client_id,
        "redirect_uri": body.redirect_uri,
        "code": body.code,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_endpoint,
            content=urlencode(body_params),
            headers={"content-type": "application/x-www-form-urlencoded"},
            auth=httpx.BasicAuth(username=identity_provider.client_id, password=identity_provider.client_secret),
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
        await db.flush()
    user.last_login = int(datetime.now().timestamp())
    await db.flush()
    return TokenResponse(
        token=encode_token(str(user.id)),
    )


@router.post("/auth/login/token")
@alog
async def exchange_token_login(body: ExchangeTokenLoginBody) -> TokenResponse:
    """Login with exchange token.

    Inout:

    - the request body

    returns:

    - the login token
    """
    user_id = decode_exchange_token(body.exchangeToken)

    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    return TokenResponse(token=encode_token(str(user_id)))


@router.put(
    "/auth/setPassword/{userId}",
    summary="Admin sets the password of the user to a new password",
)
@alog
async def change_password_UserId(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SetPasswordBody,
    user_id: Annotated[int, Path(alias="userId")],
) -> ChangeLoginInfoResponse:
    """Set the password of the user to a new password

    args:

    - the request body

    - The current database

    returns:

    - the response from the api after the password change request
    """

    return await _change_password_UserId(auth, db, user_id, body)


# --- endpoint logic ---


@alog
async def _get_oidc_config(base_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        oidc_config_response = await client.get(f"{base_url}/.well-known/openid-configuration")

    return oidc_config_response.json()


# --- endpoint logic ---
@alog
async def _get_all_open_id_connect_providers_info(db: Session) -> list[IdentityProviderInfo]:
    query = select(OIDCIdentityProvider)
    result = await db.execute(query)
    oidc_providers = result.scalars().all()

    return [
        IdentityProviderInfo(
            id=provider.id,
            name=provider.name,
            url=await get_idp_url(db, provider.id),
        )
        for provider in oidc_providers
    ]


@alog
async def get_idp_url(db: Session, identity_provider_id: int) -> str:
    identity_provider: OIDCIdentityProvider | None = await db.get(OIDCIdentityProvider, identity_provider_id)

    if not identity_provider or not identity_provider.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    oidc_config = await _get_oidc_config(identity_provider.base_url)

    query_params = {
        "scope": "openid profile email",
        "response_type": "code",
        "client_id": identity_provider.client_id,
    }

    authorization_endpoint = oidc_config["authorization_endpoint"]

    url = f"{authorization_endpoint}?{urlencode(query_params)}"
    return url


@alog
async def _get_all_open_id_connect_providers(db: Session) -> list[GetIdentityProviderResponse]:
    # if not (
    #    check_permissions(auth, [Permission.SITE_ADMIN])
    #    and check_permissions(auth, [Permission.ADMIN])
    # ):
    #    raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(OIDCIdentityProvider)
    result = await db.execute(query)
    oidc_providers = result.scalars().all()

    return [
        GetIdentityProviderResponse(
            id=provider.id,
            name=provider.name,
            org_id=provider.org_id,
            active=provider.active,
            base_url=provider.base_url,
            client_id=provider.client_id,
            scope=provider.scope,
        )
        for provider in oidc_providers
    ]


@alog
async def _get_open_id_connect_provider_by_id(auth: Auth, db: Session, provider_id: str) -> GetIdentityProviderResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(OIDCIdentityProvider).where(OIDCIdentityProvider.id == provider_id)
    result = await db.execute(query)
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="OpenID Connect provider not found")
    return GetIdentityProviderResponse(
        id=provider.id,
        name=provider.name,
        org_id=provider.org_id,
        active=provider.active,
        base_url=provider.base_url,
        client_id=provider.client_id,
        scope=provider.scope,
    )


@alog
async def _change_password_UserId(
    auth: Auth, db: Session, user_id: int, body: SetPasswordBody
) -> ChangeLoginInfoResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user.password = hash_secret(body.password.get_secret_value())
    user.change_pw = True

    await db.flush()

    return ChangeLoginInfoResponse(successful=True)


@alog
async def _add_openID_Connect_provider(auth: Auth, db: Session, body: IdentityProviderBody) -> IdentityProviderInfo:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    oidc_provider = OIDCIdentityProvider(
        name=body.name,
        org_id=body.org_id,
        active=body.active,
        base_url=body.base_url,
        client_id=body.client_id,
        client_secret=body.client_secret.get_secret_value(),
        scope=body.scope,
    )
    db.add(oidc_provider)
    await db.flush()
    await db.refresh(oidc_provider)

    return IdentityProviderInfo(id=oidc_provider.id, name=oidc_provider.name)


@alog
async def _delete_openID_Connect_provider(db: Session, open_Id_Connect_provider_Id: str) -> ChangeLoginInfoResponse:
    query = select(OIDCIdentityProvider).where(OIDCIdentityProvider.id == open_Id_Connect_provider_Id)
    oidc = await db.execute(query)
    oidc_provider = oidc.scalars().first()

    if not oidc_provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(oidc_provider)
    await db.flush()

    return ChangeLoginInfoResponse(successful=True)


@alog
async def _edit_openID_Connect_provider(
    auth: Auth, db: Session, open_Id_Connect_provider_Id: str, body: IdentityProviderEditBody
) -> ChangeLoginInfoResponse:
    if not (check_permissions(auth, [Permission.SITE_ADMIN]) and check_permissions(auth, [Permission.ADMIN])):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(OIDCIdentityProvider).where(OIDCIdentityProvider.id == open_Id_Connect_provider_Id)
    oidc = await db.execute(query)
    oidc_provider = oidc.scalars().first()

    if not oidc_provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    settings = body.model_dump(exclude_unset=True)
    settings["client_secret"] = body.client_secret.get_secret_value() if body.client_secret is not None else None

    for key in settings.keys():
        if settings[key] is not None:
            setattr(oidc_provider, key, settings[key])

    await db.flush()

    return ChangeLoginInfoResponse(successful=True)


@alog
async def _password_login(db: Session, body: PasswordLoginBody) -> TokenResponse:
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()

    if not user:
        logger.info(f"Did not find user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if user.external_auth_required:
        logger.info(f"External auth is required for user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if not verify_secret(body.password.get_secret_value(), user.password):
        logger.info(f"Password verification failed for user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if user.change_pw:
        logger.info(f"User ({body.email}) must change password")
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if user.force_logout:
        user.force_logout = False
        await db.flush()

    user.last_login = int(datetime.now().timestamp())
    await db.flush()
    return TokenResponse(token=encode_token(str(user.id)))


@alog
async def _set_own_password(db: Session, body: ChangePasswordBody) -> TokenResponse:
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()

    if body.oldPassword is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    old_password = body.oldPassword.get_secret_value()
    new_password = body.password.get_secret_value()

    if not user:
        logger.info(f"Did not find user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    if user.external_auth_required:
        logger.info(f"External auth is required for user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if not verify_secret(old_password, user.password):
        logger.info(f"Password verification failed for user with {body.email}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if old_password.lower() in new_password.lower():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    user.password = hash_secret(new_password)
    user.change_pw = False

    await db.flush()

    return TokenResponse(token=encode_token(str(user.id)))
