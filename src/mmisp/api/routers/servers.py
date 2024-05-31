import importlib
from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.db.database import Session, get_db

router = APIRouter(tags=["servers"])

@router.post("/servers/createBackup/{path}",
    status_code=status.HTTP_200_OK,
    summary="creates a backup on the given path",
    description="creates a backup of the current database if the given path is valid",
)
async def create_backup(
    //TODO
)
return await _create_backup(db, path)

@router.post("/sservers/updateBackup/{path}",
    status_code=status.HTTP_200_OK,
    summary="creates a backup on the given path",
    description="creates a backup of the current database if the given path is valid",
)
async def update_backup(
    //TODO
)
return await _update_backup(db, path)

@router.get("/servers/getVersion")
async def get_version(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return {
        "version": importlib.metadata.version("mmisp-api"),
        "perm_sync": await check_permissions(db, auth, [Permission.SYNC]),
        "perm_sighting": await check_permissions(db, auth, [Permission.SIGHTING]),
        "perm_galaxy_editor": await check_permissions(db, auth, [Permission.GALAXY_EDITOR]),
        "request_encoding": [],
        "filter_sightings": True,
    }

# --- endpoint logic ---

async def _create_backup(db: Session, str: path)

async def _update_backup(db: Session, str: path)
