import importlib
from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions

router = APIRouter(tags=["servers"])


@router.get("/servers/getVersion")
async def get_version(auth: Annotated[Auth, Depends(authorize(AuthStrategy.HYBRID))]) -> dict:
    return {
        "version": importlib.metadata.version("mmisp-api"),
        "perm_sync": check_permissions(auth, [Permission.SYNC]),
        "perm_sighting": check_permissions(auth, [Permission.SIGHTING]),
        "perm_galaxy_editor": check_permissions(auth, [Permission.GALAXY_EDITOR]),
        "request_encoding": [],
        "filter_sightings": True,
    }
