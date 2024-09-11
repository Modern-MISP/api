import importlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.organisations import BaseOrganisation
from mmisp.api_schemas.responses.standard_status_response import StandardStatusIdentifiedResponse
from mmisp.api_schemas.servers import (
    AddServer,
    AddServerResponse,
    AddServerServer,
    EditServer,
    GetRemoteServer,
    ServerResponse,
)
from mmisp.db.database import Session, get_db
from mmisp.db.models.server import Server

router = APIRouter(tags=["servers"])


@router.get(
    "/servers/remote/getAll",
    summary="Requests a list of all remote servers",
)
async def get_remote_servers(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetRemoteServer]:
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
async def get_remote_server_by_id(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    server_Id: Annotated[str, Path(alias="serverId")],
) -> GetRemoteServer:
    """
    Returns information for a specific remote server chosen by its id.

    Input:

    - serverId: the server's ID

    - The current database

    Output:

    - server information regarding the chosen server
    """
    return await _get_remote_server_by_id(auth, db, server_Id)


@router.post(
    "/servers/remote/add",
    summary="Adds a new remote server to the list",
)
async def add_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddServer,
) -> AddServerResponse:
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
    "/servers/remote/delete/{server_id}",
    summary="Deletes a remote server by id",
)
async def delete_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    server_id: Annotated[str, Path(alias="server_id")],
) -> StandardStatusIdentifiedResponse:
    """
    Deletes a remote server if the given id is valid.

    Input:

    - Identifier of the remote server to be deleted

    - The current database

    Output:

    - Response indicating the result of the server deletion operation
    """
    return await _delete_remote_server(auth=auth, db=db, server_id=server_id)


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


@router.post(
    "/servers/remote/edit/{server_id}",
    summary="Edits remote servers",
)
async def update_remote_server(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    server_id: Annotated[str, Path(alias="server_id")],
    body: EditServer,
) -> AddServerResponse:
    """
    Edits servers given by org_id.

    Input:

    - org_id

    - The current database

    - auth: Authentication details

    Output:

    - Updated servers as a list
    """
    return await _edit_server_by_id(auth=auth, db=db, server_id=server_id, body=body)


# --- deprecated ---


@router.get(
    "/servers/",
    deprecated=True,
    summary="Requests a list of all remote servers",
)
async def get_remote_servers_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
) -> list[GetRemoteServer]:
    """Deprecated
    Returns a list of all currently active remote servers.

    Input:

    - The current database

    Output:

    - List of remote servers
    """
    return await _get_remote_servers(auth, db)


@router.post(
    "/servers/add",
    deprecated=True,
    summary="Adds a new remote server to the list",
)
async def add_remote_server_depr(
    auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))],
    db: Annotated[Session, Depends(get_db)],
    body: AddServer,
) -> AddServerResponse:
    """
    Adds a new remote server based on the input of an admin.

    Input:

    - Data containing details of the remote server to be added
    - The current database

    Output:

    - Response indicating the result of the server addition operation
    """
    return await _add_remote_server(auth, db, body)


# --- endpoint logic ---


async def _get_remote_servers(auth: Auth, db: Session) -> list[GetRemoteServer]:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(Server).options(
        selectinload(Server.remote_organisation), selectinload(Server.organisation), selectinload(Server.users)
    )
    result = await db.execute(query)
    servers = result.scalars().all()

    return [get_remote_server_answer(server) for server in servers]


def get_remote_server_answer(server: Server) -> GetRemoteServer:
    server_dict = server.__dict__.copy()
    server_dict["lastpulledid"] = server_dict.pop("last_pulled_id")
    server_dict["lastpushedid"] = server_dict.pop("last_pushed_id")

    org_dict = server.organisation.__dict__.copy()
    if server.remote_organisation is not None:
        remote_org_dict = server.remote_organisation.__dict__.copy()
    else:
        remote_org_dict = {
            "id": None,
            "name": None,
            "type": None,
            "uuid": None,
        }

    users_list_dict = [user.__dict__.copy() for user in server.users]

    return GetRemoteServer(
        Server=ServerResponse(**server_dict),
        Organisation=BaseOrganisation(**org_dict),
        RemoteOrg=BaseOrganisation(**remote_org_dict),
        User=users_list_dict,
    )


async def _get_remote_server_by_id(auth: Auth, db: Session, serverId: str) -> GetRemoteServer:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = (
        select(Server)
        .options(
            selectinload(Server.remote_organisation), selectinload(Server.organisation), selectinload(Server.users)
        )
        .where(Server.id == serverId)
    )

    result = await db.execute(query)
    server = result.scalar_one_or_none()

    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Remote server not found")

    return get_remote_server_answer(server)


async def _add_remote_server(auth: Auth, db: Session, body: AddServer) -> AddServerResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if body.org_id is None:
        body.org_id = auth.org_id

    server = Server(
        name=body.name,
        url=body.url,
        priority=body.priority,
        authkey=body.authkey,
        org_id=body.org_id,
        remote_org_id=body.remote_org_id,
        internal=body.internal,
        push=body.push,
        pull=body.pull,
        pull_rules=body.pull_rules.json().replace(" ", ""),
        push_rules=body.push_rules.json().replace(" ", ""),
        push_galaxy_clusters=body.push_galaxy_clusters,
        caching_enabled=body.caching_enabled,
        unpublish_event=body.unpublish_event,
        publish_without_email=body.publish_without_email,
        self_signed=body.self_signed,
        skip_proxy=body.skip_proxy,
    )
    db.add(server)
    await db.commit()
    await db.refresh(server)

    server_dict = server.__dict__.copy()

    return AddServerResponse(Server=AddServerServer(**server_dict))


async def _delete_remote_server(auth: Auth, db: Session, server_id: str) -> StandardStatusIdentifiedResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    server_to_delete = await db.get(Server, server_id)

    if not server_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remote server not found")

    # Delete
    await db.delete(server_to_delete)
    await db.commit()

    return StandardStatusIdentifiedResponse(
        saved=True,
        success=True,
        name="Remote server deleted.",
        message="Remote server deleted successfully.",
        url=f"/servers/remote/delete/{server_id}",
        id=server_id,
    )


async def _edit_server_by_id(auth: Auth, db: Session, server_id: str, body: EditServer) -> AddServerResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(Server).where(Server.id == server_id)
    result = await db.execute(query)
    server = result.scalars().one_or_none()

    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    server.name = body.name
    server.url = body.url
    server.priority = body.priority
    server.authkey = body.authkey
    server.remote_org_id = body.remote_org_id
    server.internal = body.internal
    server.push = body.push
    server.pull = body.pull
    server.pull_rules = body.pull_rules.json().replace(" ", "")
    server.push_rules = body.push_rules.json().replace(" ", "")
    server.push_galaxy_clusters = body.push_galaxy_clusters
    server.caching_enabled = body.caching_enabled
    server.unpublish_event = body.unpublish_event
    server.publish_without_email = body.publish_without_email
    server.self_signed = body.self_signed
    server.skip_proxy = body.skip_proxy

    db.add(server)
    await db.commit()
    await db.refresh(server)

    server_dict = server.__dict__.copy()

    return AddServerResponse(Server=AddServerServer(**server_dict))
