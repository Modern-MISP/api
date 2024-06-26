import importlib
from typing import Annotated

from fastapi import APIRouter, Depends

from mmisp.api.auth import Auth, AuthStrategy, Permission, authorize, check_permissions
from mmisp.db.database import Session, get_db

router = APIRouter(tags=["servers"])


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
