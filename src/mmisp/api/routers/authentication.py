from collections.abc import Sequence
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
from mmisp.api.config import config
from mmisp.api_schemas.authentication import (
    ChangeLoginInfoResponse,
    ChangePasswordBody,
    ExchangeTokenLoginBody,
    GetIdentityProviderResponse,
    IdentityProviderBody,
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
from mmisp.util.crypto import hash_secret, verify_secret

router = APIRouter(tags=["authentication"])


@router.get("/auth/openID/getAllOpenIDConnectProvidersInfo")
async def get_all_open_id_connect_providers_info(
    db: Annotated[Session, Depends(get_db)],
) -> list[IdentityProviderInfo]:
    """
    Fetches all OpenID Connect providers

    Input:
    - Authorization token
    - Database session

    Output:
    - List of OpenID Connect providers
    """
    return await _get_all_open_id_connect_providers_info(db)


@router.get("/auth/openID/getAllOpenIDConnectProviders")
async def get_all_open_id_connect_providers(
    db: Annotated[Session, Depends(get_db)],
) -> list[GetIdentityProviderResponse]:
    """
    Fetches all OpenID Connect providers

    Input:
    - Authorization token
    - Database session

    Output:
    - List of OpenID Connect providers
    """
    return await _get_all_open_id_connect_providers(db)


@router.get("/auth/openID/getOpenIDConnectProvider/{providerId}")
async def get_open_id_connect_provider_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    provider_id: Annotated[str, Path(alias="providerId")],
) -> GetIdentityProviderResponse:
    """
    Fetches a single OpenID Connect provider by its ID

    Input:
    - Authorization token
    - Database session
    - Provider ID

    Output:
    - OpenID Connect provider details
    """
    return await _get_open_id_connect_provider_by_id(auth, db, provider_id)


@router.post("/auth/openID/addOpenIDConnectProvider")
async def add_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: IdentityProviderBody,
) -> IdentityProviderInfo:
    """Adds a new OpenID Connect provider

    Input:

    - database

    Output:

    - openID Connect provider
    """
    return await _add_openID_Connect_provider(auth, db, body)


@router.post("/auth/openID/editOpenIDConnectProvider/{openIDConnectProvider}")
async def edit_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    open_Id_Connect_provider_Id: Annotated[str, Path(alias="openIDConnectProvider")],
    body: IdentityProviderEditBody,
) -> ChangeLoginInfoResponse:
    """Edits an OpenID Connect provider

    Input:

    - OpenID Connect provider

    - The current database

    Output:

    - updated OpenID Connect provider
    """
    return await _edit_openID_Connect_provider(auth, db, open_Id_Connect_provider_Id, body)


@router.delete(
    "/auth/openID/delete/{openIDConnectProvider}",
    summary="Deletes an OpenID Connect Provider by its ID",
)
async def delete_openID_Connect_provider(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    open_Id_Connect_provider_Id: Annotated[str, Path(alias="openIDConnectProvider")],
) -> ChangeLoginInfoResponse:
    """Deletes an OpenID Connect provider

    Input:

    - OpenID Connect provider

    - The current database

    Output:

    - database
    """
    return await _delete_openID_Connect_provider(db, open_Id_Connect_provider_Id)


@router.post("/auth/login/start", response_model=StartLoginResponse)
async def start_login(db: Annotated[Session, Depends(get_db)], body: StartLoginBody) -> dict:
    """Starts the login process.

    Input:

    - the database

    - the request body

    Output:

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
async def password_login(db: Annotated[Session, Depends(get_db)], body: PasswordLoginBody) -> TokenResponse:
    """Login with password.

    Input:

    - the database

    - the request body

    Output:

    - the login token
    """
    return await _password_login(db, body)


@router.post(
    "/auth/login/setOwnPassword",
    summary="User sets their password to a new password",
)
async def set_password(
    db: Annotated[Session, Depends(get_db)],
    body: ChangePasswordBody,
) -> TokenResponse:
    """Sets the password of the user to a new password.

    Input:

    - the database

    Output:

    - the response form the api after the password change request
    """
    return await _set_own_password(db, body)


@router.get("/auth/login/idp/{identityProviderName}/callback")
@router.post("/auth/login/idp/{identityProviderName}/callback")
async def redirect_to_frontend(
    db: Annotated[Session, Depends(get_db)],
    identity_provider_name: Annotated[str, Path(alias="identityProviderName")],
    code: str,
) -> TokenResponse:
    """Redirects to the frontend.

    Input:

    - the database

    - the identity provider id

    - the code

    Output:

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
        "redirect_uri": f"{config.OWN_URL}/login/oidc/{identity_provider.name}/callback",
        "code": code,
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
    print(user_info)

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
        await db.commit()

    return TokenResponse(
        token=encode_token(str(user.id)),
    )


@router.post("/auth/login/token")
async def exchange_token_login(body: ExchangeTokenLoginBody) -> TokenResponse:
    """Login with exchange token.

    Inout:

    - the request body

    Output:

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
async def change_password_UserId(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: SetPasswordBody,
    user_id: Annotated[int, Path(alias="userId")],
) -> ChangeLoginInfoResponse:
    """Set the password of the user to a new password

    Input:

    - the request body

    - The current database

    Output:

    - the response from the api after the password change request
    """

    return await _change_password_UserId(auth, db, user_id, body)


# --- endpoint logic ---


async def _get_oidc_config(base_url: str) -> dict:
    async with httpx.AsyncClient() as client:
        oidc_config_response = await client.get(f"{base_url}/.well-known/openid-configuration")

    return oidc_config_response.json()


# --- endpoint logic ---
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


async def get_idp_url(db: Session, identity_provider_id: int) -> str:
    identity_provider: OIDCIdentityProvider | None = await db.get(OIDCIdentityProvider, identity_provider_id)

    if not identity_provider or not identity_provider.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    oidc_config = await _get_oidc_config(identity_provider.base_url)

    query_params = {
        "scope": "openid profile email",
        "response_type": "code",
        "client_id": identity_provider.client_id,
        "redirect_uri": f"{config.OWN_URL}/login/oidc/{identity_provider.name}/callback",
    }

    authorization_endpoint = oidc_config["authorization_endpoint"]

    url = f"{authorization_endpoint}?{urlencode(query_params)}"
    return url


async def _get_all_open_id_connect_providers(db: Session) -> list[GetIdentityProviderResponse]:
    # if not (
    #    await check_permissions(db, auth, [Permission.SITE_ADMIN])
    #    and await check_permissions(db, auth, [Permission.ADMIN])
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
            client_secret=provider.client_secret,
            scope=provider.scope,
        )
        for provider in oidc_providers
    ]


async def _get_open_id_connect_provider_by_id(auth: Auth, db: Session, provider_id: str) -> GetIdentityProviderResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
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
        client_secret=provider.client_secret,
        scope=provider.scope,
    )


"""async def _get_password_requirements(db: Session) -> :
    return RequirementResponse()"""


async def _change_password_UserId(
    auth: Auth, db: Session, user_id: int, body: SetPasswordBody
) -> ChangeLoginInfoResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user.password = hash_secret(body.password)
    user.change_pw = True

    await db.commit()

    return ChangeLoginInfoResponse(successful=True)


async def _add_openID_Connect_provider(auth: Auth, db: Session, body: IdentityProviderBody) -> IdentityProviderInfo:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    oidc_provider = OIDCIdentityProvider(
        name=body.name,
        org_id=body.org_id,
        active=body.active,
        base_url=body.base_url,
        client_id=body.client_id,
        client_secret=body.client_secret,
        scope=body.scope,
    )
    db.add(oidc_provider)
    await db.commit()
    await db.refresh(oidc_provider)

    return IdentityProviderInfo(id=oidc_provider.id, name=oidc_provider.name)


async def _delete_openID_Connect_provider(db: Session, open_Id_Connect_provider_Id: str) -> ChangeLoginInfoResponse:
    query = select(OIDCIdentityProvider).where(OIDCIdentityProvider.id == open_Id_Connect_provider_Id)
    oidc = await db.execute(query)
    oidc_provider = oidc.scalars().first()

    if not oidc_provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    await db.delete(oidc_provider)
    await db.commit()

    return ChangeLoginInfoResponse(successful=True)


async def _edit_openID_Connect_provider(
    auth: Auth, db: Session, open_Id_Connect_provider_Id: str, body: IdentityProviderEditBody
) -> ChangeLoginInfoResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(OIDCIdentityProvider).where(OIDCIdentityProvider.id == open_Id_Connect_provider_Id)
    oidc = await db.execute(query)
    oidc_provider = oidc.scalars().first()

    if not oidc_provider:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    settings = body.dict(exclude_unset=True)

    for key in settings.keys():
        if settings[key] is not None:
            setattr(oidc_provider, key, settings[key])

    await db.commit()

    return ChangeLoginInfoResponse(successful=True)


async def _password_login(db: Session, body: PasswordLoginBody) -> TokenResponse:
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()

    if not user or user.external_auth_required or not verify_secret(body.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if user.change_pw:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    if user.force_logout:
        user.force_logout = False
        await db.commit()

    return TokenResponse(token=encode_token(str(user.id)))


async def _set_own_password(db: Session, body: ChangePasswordBody) -> TokenResponse:
    result = await db.execute(select(User).filter(User.email == body.email).limit(1))
    user: User | None = result.scalars().first()
    old_password = body.oldPassword

    if old_password is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if not user or user.external_auth_required or not verify_secret(old_password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if old_password.lower() in body.password.lower():
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    user.password = hash_secret(body.password)
    user.change_pw = False

    await db.commit()

    return TokenResponse(token=encode_token(str(user.id)))
