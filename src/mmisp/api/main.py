from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from mmisp.db.database import Base, engine

# if you add a new model module, add it here too
from mmisp.db.models import (  # noqa: F401
    attribute,
    event,
    feed,
    galaxy,
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
    warninglist,
)
from mmisp.db.models import (  # noqa: F401
    auth_key as auth_key_model,
)
from mmisp.db.models import (  # noqa: F401
    user_settings as user_settings_model,
)

from .routers import (
    attributes,
    auth_key,
    authentication,
    events,
    feeds,
    # galaxies,
    jobs,
    noticelists,
    objects,
    sharing_groups,
    sightings,
    tags,
    user_settings,
    users,
    warninglists,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# include Routes
app.include_router(attributes.router)
app.include_router(auth_key.router)
app.include_router(events.router)
app.include_router(user_settings.router)
app.include_router(feeds.router)
# app.include_router(galaxies.router)
app.include_router(objects.router)
app.include_router(sightings.router)
app.include_router(tags.router)
app.include_router(sharing_groups.router)
app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(jobs.router)
app.include_router(warninglists.router)
app.include_router(noticelists.router)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
