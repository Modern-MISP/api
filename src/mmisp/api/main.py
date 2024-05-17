from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# if you add a new model module, add it here too
import mmisp.db.all_models  # noqa: F401
from mmisp.db.database import create_all_models, sessionmanager

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


def init_app(init_db: bool = True) -> FastAPI:
    lifespan: Callable | None = None

    if init_db:
        sessionmanager.init()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        await create_all_models()
        yield
        if sessionmanager._engine is not None:
            await sessionmanager.close()

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    return app


app = init_app()
