from fastapi import APIRouter
from mmisp.api_schemas.users.users_view_me_response import UsersViewMeResponse


router = APIRouter(tags=["users"])


@router.get("/users/view/me")
async def get_logged_in_user_info() -> UsersViewMeResponse:
    return UsersViewMeResponse()
