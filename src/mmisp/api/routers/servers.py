import importlib
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.db.database import Session, get_db

router = APIRouter(tags=["servers"])


@router.post(
    "/servers/updateBackup/{path}",
    summary="Updates a backup on the given path",
)
async def update_backup(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    path: Annotated[str, Path(alias="path")],
) -> None:
    """
    Updates a backup of the current database if the given path is valid.

    Input:

    - path: Path where the backup will be updated

    - The current database

    Output:

    - Response indicating the result of the backup update operation
    """
    return await _update_backup(auth, db, path)


@router.get(
    "/servers/remote/getAll",
    summary="Requests a list of all remote servers",
)
async def get_remote_servers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Returns a list of all currently active remote servers.

    Input:

    - The current database

    Output:

    - List of remote servers
    """
    return await _get_remote_servers(auth, db)


@router.get(
    "/servers/remote/{serverId}",
    summary="Requests information regarding a remote server",
)
async def get_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    server_Id: Annotated[str, Path(alias="serverId")],
) -> None:
    """
    Returns information for a specific remote server chosen by its id.

    Input:

    - serverId: the server's ID

    - The current database

    Output:

    - server information regarding the chosen server
    """
    return await _get_remote_server(auth, db, server_Id)


@router.post(
    "/servers/remote/add",
    summary="Adds a new remote server to the list",
)
async def add_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: None,
) -> None:
    """
    Adds a new remote server based on the input of an admin.

    Input:

    - Data containing details of the remote server to be added

    - The current database

    Output:

    - Response indicating the result of the server addition operation
    """
    return await _add_remote_server(auth, db, body)


@router.delete(
    "/servers/remote/delete/{serverId}",
    summary="Deletes a remote server by id",
)
async def delete_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],  #
    server_Id: Annotated[str, Path(alias="serverId")],
) -> None:
    """
    Deletes a remote server if the given id is valid.

    Input:

    - Identifier of the remote server to be deleted

    - The current database

    Output:

    - Response indicating the result of the server deletion operation
    """
    return await _delete_remote_server(auth, db, server_Id)


@router.get("/servers/getVersion")
async def get_version(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))], db: Annotated[Session, Depends(get_db)]
) -> dict:
    """
    Gets the Version of the server.

    Input:

    - auth: Authentication details

    - db: Database session

     Output:

    - Version of the server
    - Permissions for sync, sighting, and galaxy editor
    - Request encoding
    - Filter sightings flag
    """
    return {
        "version": importlib.metadata.version("mmisp-api"),
        "perm_sync": await check_permissions(db, auth, [Permission.SYNC]),
        "perm_sighting": await check_permissions(db, auth, [Permission.SIGHTING]),
        "perm_galaxy_editor": await check_permissions(db, auth, [Permission.GALAXY_EDITOR]),
        "request_encoding": [],
        "filter_sightings": True,
    }


# --- endpoint logic ---



async def _update_backup(auth: Auth, db: Session, path: str) -> None:
    return None


async def _get_remote_servers(auth: Auth, db: Session) -> None:
    return None


async def _get_remote_server(auth: Auth, db: Session, serverId: str) -> None:
    return None


async def _add_remote_server(auth: Auth, db: Session, body: None) -> None:
    return None


async def _delete_remote_server(auth: Auth, db: Session, serverId: str) -> None:
    return None
