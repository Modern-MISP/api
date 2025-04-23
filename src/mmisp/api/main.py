import importlib.resources
import itertools
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import mmisp.db.all_models  # noqa: F401
from mmisp.api.config import config
from mmisp.api.exception_handler import register_exception_handler
from mmisp.api.middleware import DryRunMiddleware, LogMiddleware
from mmisp.db.config import config as db_config
from mmisp.db.database import sessionmanager

if config.ENABLE_PROFILE:
    from mmisp.api.profile_middleware import ProfileMiddleware

router_pkg = "mmisp.api.routers"
all_routers = (
    resource.name[:-3]
    for resource in importlib.resources.files(router_pkg).iterdir()
    if resource.is_file()
    and resource.name != "__init__.py"
    and (resource.name != "test_endpoints.py" or config.ENABLE_TEST_ENDPOINTS)
)

router_module_names = map(".".join, zip(itertools.repeat(router_pkg), all_routers))

fastapi_routers = []
for m in router_module_names:
    mod = importlib.import_module(m)
    fastapi_routers.append(mod.router)


def init_app(*, init_db: bool = False) -> FastAPI:
    if db_config.CONNECTION_INIT:
        assert sessionmanager is not None
        sessionmanager.init()

    if init_db:

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator:
            assert sessionmanager is not None
            await sessionmanager.create_all()
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()
    else:
        lifespan = None  # type: ignore

    app = FastAPI(
        title="Modern MISP API",
        version=version("mmisp-api"),
        lifespan=lifespan,
        #        default_response_class=ORJSONResponse,
        debug=config.DEBUG,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-result-count", "x-worker-name-header", "x-queue-name-header"],
    )
    app.add_middleware(DryRunMiddleware)
    app.add_middleware(LogMiddleware)
    if config.ENABLE_PROFILE:
        app.add_middleware(ProfileMiddleware)

    # include Routes
    for r in fastapi_routers:
        app.include_router(r)

    register_exception_handler(app)

    # flush logger once

    return app


app = init_app()
