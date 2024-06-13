import importlib
from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions

from mmisp.db.database import Session, get_db

router = APIRouter(tags=["servers"])

@router.post("/servers/createBackup/{path}",
    summary="Creates a backup on the given path",
    description="Creates a backup of the current database if the given path is valid",
)
async def create_backup(
    TODO
) : return await _create_backup(db, path)

@router.post("/sservers/updateBackup/{path}",
    summary="Creates a backup on the given path",
    description="Creates a backup of the current database if the given path is valid",
)
async def update_backup(
    TODO
) : return await _update_backup(db, path)

@router.get("/servers/remote/getAll",
    summary="Requests a list of all remote servers",
    description="Returns a list of all currently active remote servers",
    )
async def get_remote_servers(
    TODO
) : return await _get_remote_servers(db)

@router.post("/servers/remote/add",
    summary="Adds a new remote server to the list",
    description="Adds a new remote server based on the input of an admin",
    )
async def add_remote_server(
    TODO
) : return await _add_remote_server(auth, db, body)

@router.delete("/servers/remote/delete/{serverId}",
    summary="Deletes a remote server by id",
    description="Deletes a remote server if the given id is valid",
    )
async def delete_remote_server(
    TODO
) : return await _delete_remote_server(db, serverId)

@router.get("/servers/getVersion")
async def get_version(auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],db: Annotated[Session, Depends(get_db)]) -> dict:
    return {
        "version": importlib.metadata.version("mmisp-api"),
        "perm_sync": await check_permissions(db, auth, [Permission.SYNC]),
        "perm_sighting": await check_permissions(db, auth, [Permission.SIGHTING]),
        "perm_galaxy_editor": await check_permissions(db, auth, [Permission.GALAXY_EDITOR]),
        "request_encoding": [],
        "filter_sightings": True,
    }

# --- endpoint logic ---

async def _create_backup(db: Session, path: str) : return None

async def _update_backup(db: Session, path: str) : return None

async def _get_remote_servers(db: Session) : return None

async def _add_remote_server(PLACEHOLDER) : return None

async def _delete_remote_server(db: Session, serverId: str): return None

