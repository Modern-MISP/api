import importlib
import importlib.resources
import itertools
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

import mmisp.db.all_models  # noqa: F401
from mmisp.api.config import config
from mmisp.api.exception_handler import register_exception_handler
from mmisp.db.database import sessionmanager

if config.ENABLE_PROFILE:
    from mmisp.api.profile_middleware import ProfileMiddleware

router_pkg = "mmisp.api.routers"
all_routers = (
    resource.name[:-3]
    for resource in importlib.resources.files(router_pkg).iterdir()
    if resource.is_file() and resource.name != "__init__.py"
)

router_module_names = map(".".join, zip(itertools.repeat(router_pkg), all_routers))

fastapi_routers = []
for m in router_module_names:
    mod = importlib.import_module(m)
    fastapi_routers.append(mod.router)


def init_app(*, init_db: bool = False) -> FastAPI:
    sessionmanager.init()

    if init_db:

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator:
            await sessionmanager.create_all()
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()
    else:
        lifespan = None  # type: ignore

    app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if config.ENABLE_PROFILE:
        app.add_middleware(ProfileMiddleware)

    # include Routes
    for r in fastapi_routers:
        app.include_router(r)

    register_exception_handler(app)

    return app


app = init_app()
