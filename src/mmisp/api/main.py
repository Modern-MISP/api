from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from mmisp.db.database import create_all_models

# if you add a new model module, add it here too
from mmisp.db.models import (  # noqa: F401
    attribute,
    auth_key,
    event,
    feed,
    galaxy,
    identity_provider,
    noticelist,
    object,
    organisation,
    role,
    server,
    sharing_group,
    sighting,
    tag,
    taxonomy,
    user,
    user_setting,
    warninglist,
)

from .routers import (
    attributes,
    auth_keys,
    authentication,
    events,
    feeds,
    galaxies,
    jobs,
    noticelists,
    objects,
    servers,
    sharing_groups,
    sightings,
    tags,
    taxonomies,
    user_settings,
    users,
    warninglists,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await create_all_models()
    yield


app = FastAPI(lifespan=lifespan)

# include Routes
app.include_router(attributes.router)
app.include_router(auth_keys.router)
app.include_router(events.router)
app.include_router(user_settings.router)
app.include_router(feeds.router)
app.include_router(galaxies.router)
app.include_router(objects.router)
app.include_router(sightings.router)
app.include_router(tags.router)
app.include_router(taxonomies.router)
app.include_router(servers.router)
app.include_router(sharing_groups.router)
app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(jobs.router)
app.include_router(warninglists.router)
app.include_router(noticelists.router)
