from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api_schemas.users import UsersViewMeResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.util.partial import partial

from ..auth import Auth, AuthStrategy, authorize

router = APIRouter(tags=["users"])

@router.post(
    "/users",
    status_code=status.HTTP_200_OK,
    response_model=PLACEHOLDER,
    summary="Add new user",
    description="Add a new user with the given details.",
)
async def add_user(
    //TODO
)
    return await _add_user(db, user)


@router.get(
    "/users/view/all",
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Retrieve a list of all users.",
)
async def get_all_users(
   //TODO
) 
    return await _get_all_users(db)

@router.get(
    "/users/view/{userId}",
    status_code=status.HTTP_200_OK,
    summary="Get a user by id",
    description="Retrieve a user specified by id.",
)
async def get_user_by_id(
   //TODO
)
    return await _get_user(db, userId)

@router.delete(
    "/users/{userId}",
    status_code=status.HTTP_200_OK,
    response_model=PLACEHOLDER,
    summary="Delete a user",
    description="Delete a user by their ID.",
)
async def delete_user(
    //TODO
)
    return await _delete_user(db, userID)

@router.delete(
    "/users/{userId}",
    status_code=status.HTTP_200_OK,
    response_model=PLACEHOLDER,
    summary="Delete a users login token",
    description="Delete a users login token by their ID.",
)
async def delete_user_token(
    //TODO
)
    return await _delete_user_token(db, userID)

@router.put(
    "/users/{userId}",
    status_code=status.HTTP_200_OK,
    response_model=PLACEHOLDER,
    summary="Update a user",
    description="Update an existing user by their ID.",
)
async def update_user(
    //TODO
) 
    return await _update_user(db, userID)



@router.get("/users/view/me.json", response_model=partial(UsersViewMeResponse))
@router.get("/users/view/me", response_model=partial(UsersViewMeResponse))
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> dict:
    user = await db.get(User, auth.user_id)
    organisation = await db.get(Organisation, auth.org_id)
    role = await db.get(Role, auth.role_id)

    return {"User": user.__dict__, "Organisation": organisation.__dict__, "Role": role.__dict__}

# --- endpoint logic ---

async def _add_user(db: Session, user: user)

async def _get_all_users(db: Session)

async def _get_user(db: Session, userID: str)

async def _delete_user(db: Session, userID: str)

async def _delete_user_token(db: Session, userID: str)

async def _update_user(db: Session, userID: str)