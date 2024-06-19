from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api_schemas.users import UsersViewMeResponse, UserAttributesResponse
from mmisp.db.database import Session, get_db
from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.db.models.user import User
from mmisp.util.partial import partial

from ..auth import Auth, AuthStrategy, authorize

router = APIRouter(tags=["users"])

@router.post(
    "/users",
    #response_model=UserAttributesResponse,
    summary="Add new user",
)
async def add_user(
    TODO
) :
    """
    Adds a new user with the given details.

    Input:
    - Data representing the new user to be added
    
    Output:
    - Data representing the attributes of the new user
    """
    return await _add_user(db, user)

@router.get("/users/view/me.json", response_model=partial(UsersViewMeResponse))
@router.get("/users/view/me", response_model=partial(UsersViewMeResponse))
async def get_logged_in_user_info(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Retrieves information about the logged in user.

    Input:
    - Authentication details of the logged in user
    
    Output:
    - Information about the logged in user
    """
    user = await db.get(User, auth.user_id)
    organisation = await db.get(Organisation, auth.org_id)
    role = await db.get(Role, auth.role_id)

    return {"User": user.__dict__, "Organisation": organisation.__dict__, "Role": role.__dict__}

@router.get(
    "/users/view/all",
    summary="Get all users",
)
async def get_all_users(
   TODO
) :
    """
    Retrieves a list of all users.

    Input:
    - None
    
    Output:
    - List containing all users
    """
    return await _get_all_users(db)

@router.get(
    "/users/view/{userId}",
    summary="Get a user by id",
)
async def get_user_by_id(
   TODO
) :
    """
    Retrieves a user specified by id.

    Input:
    - ID of the user to get
    
    Output:
    - Data representing the attributes of the searched user
    """
    return await _get_user(db, userId)

@router.delete(
    "/users/{userId}",
    #response_model=UserAttributesResponse,
    summary="Delete a user",
)
async def delete_user(
    TODO
) :
    """
    Deletes a user by their ID.

    Input:
    - ID of the user to delete
    
    Output:
    - Response indicating success or failure
    """
    return await _delete_user(db, userID)

@router.delete(
    "/users/{userId}",
    #response_model=UserAttributesResponse,
    summary="Delete a users login token",
)
async def delete_user_token(
    TODO
) :
    """
    Deletes a users login token by their ID.

    Input:
    -ID of the user with the token to delete
    
    Output:
    - Response indicating success or failure
    """
    return await _delete_user_token(db, userID)

@router.put(
    "/users/{userId}",

    #response_model=UserAttributesResponse,
    summary="Update a user",
)
async def update_user(
    TODO
) :
    """
    Updates an existing user by their ID.

    Input:
    - ID of the user to update
    - Updated data for the user
    
    Output:
    - Data representing the updated attributes of the user
    """
    return await _update_user(db, userID)

# --- endpoint logic ---

async def _add_user(db: Session, user: User) : return None
#Adds a new user and generates a new single-time password

async def _get_all_users(db: Session) : return None

async def _get_user(db: Session, userID: str) : return None

async def _delete_user(db: Session, userID: str) : return None

async def _delete_user_token(db: Session, userID: str) : return None

async def _update_user(db: Session, userID: str) : return None

