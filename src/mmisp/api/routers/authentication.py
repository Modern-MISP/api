from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from mmisp.api_schemas.authentication.exchange_token_login_body import ExchangeTokenLoginBody
from mmisp.api_schemas.authentication.password_login_body import PasswordLoginBody
from mmisp.api_schemas.authentication.start_login_body import StartLoginBody
from mmisp.api_schemas.authentication.start_login_response import StartLoginResponse
from mmisp.api_schemas.authentication.token_response import TokenResponse

router = APIRouter(tags=["authentication"])


@router.post("/auth/login/start")
async def start_login(body: StartLoginBody) -> StartLoginResponse:
    return StartLoginResponse()


@router.post("/auth/login/password")
async def password_login(body: PasswordLoginBody) -> TokenResponse:
    return TokenResponse()


@router.get("/auth/login/idp/{identityProviderId}/authorize", response_class=RedirectResponse)
async def redirect_to_idp(identityProviderId: str):
    return RedirectResponse(url="", status_code=302)


# TODO define query schema
@router.get("/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse)
@router.post("/auth/login/idp/{identityProviderId}/callback", response_class=RedirectResponse)
async def redirect_to_frontend(identityProviderId: str) -> RedirectResponse:
    return RedirectResponse(url="frontend_url?exchangeToken=generated_token", status_code=302)


@router.post("/auth/login/token")
async def exchange_token_login(body: ExchangeTokenLoginBody) -> TokenResponse:
    return TokenResponse()
