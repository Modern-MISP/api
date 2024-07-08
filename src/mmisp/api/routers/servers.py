import importlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.future import select

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.api_schemas.servers import AddServer, AddServerResponse, GetRemoteServersResponse
from mmisp.api_schemas.standard_status_response import StandardStatusIdentifiedResponse
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
) -> list[GetRemoteServersResponse]:
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
) -> GetRemoteServersResponse:
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


# --- endpoint logic ---


async def _get_remote_servers(auth: Auth, db: Session) -> list[GetRemoteServersResponse]:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(Server)
    result = await db.execute(query)
    servers = result.fetchall()
    server_list_computed: list[GetRemoteServersResponse] = []

    for server in servers:
        server_list_computed.append(
            GetRemoteServersResponse(
                id=server[0].id,
                name=server[0].name,
                url=server[0].url,
                authkey=server[0].authkey,
                org_id=server[0].org_id,
                push=server[0].push,
                pull=server[0].pull,
                push_sightings=server[0].push_sightings,
                push_galaxy_clusters=server[0].push_galaxy_clusters,
                pull_galaxy_clusters=server[0].pull_galaxy_clusters,
                remote_org_id=server[0].remote_org_id,
                publish_without_email=server[0].publish_without_email,
                unpublish_event=server[0].unpublish_event,
                self_signed=server[0].self_signed,
                internal=server[0].internal,
                skip_proxy=server[0].skip_proxy,
                caching_enabled=server[0].caching_enabled,
                priority=server[0].priority,
            )
        )

    return server_list_computed


async def _get_remote_server_by_id(auth: Auth, db: Session, serverId: str) -> GetRemoteServersResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        or await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    query = select(Server).where(Server.id == serverId)
    result = await db.execute(query)
    server = result.scalar_one_or_none()

    if server is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Remote server not found")

    return GetRemoteServersResponse(
        id=server.id,
        name=server.name,
        url=server.url,
        authkey=server.authkey,
        org_id=server.org_id,
        push=server.push,
        pull=server.pull,
        push_sightings=server.push_sightings,
        push_galaxy_clusters=server.push_galaxy_clusters,
        pull_galaxy_clusters=server.pull_galaxy_clusters,
        remote_org_id=server.remote_org_id,
        publish_without_email=server.publish_without_email,
        unpublish_event=server.unpublish_event,
        self_signed=server.self_signed,
        internal=server.internal,
        skip_proxy=server.skip_proxy,
        caching_enabled=server.caching_enabled,
        priority=server.priority,
    )


async def _add_remote_server(auth: Auth, db: Session, body: AddServer) -> StandardStatusIdentifiedResponse:
    if not (
        await check_permissions(db, auth, [Permission.SITE_ADMIN])
        and await check_permissions(db, auth, [Permission.ADMIN])
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    server = Server(
        name=body.name,
        url="default_url",
        priority=1,
        authkey="default_authkey",
        org_id=2,
        remote_org_id=3,
        internal=False,
        push=False,
        pull=False,
        pull_rules="default_pull_rules",
        push_rules="default_push_rules",
        push_galaxy_clusters=False,
        caching_enabled=False,
        unpublish_event=False,
        publish_without_email=False,
        self_signed=False,
        skip_proxy=False,
    )
    db.add(server)
    await db.commit()
    await db.refresh(server)

    return AddServerResponse(
        id=server.id,
    )


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
