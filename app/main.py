from fastapi import FastAPI

from .database import engine
from .models.feed import Base
from .routers import (
    attributes,
    auth_key,
    events,
    feeds,
    galaxies,
    objects,
    sightings,
    tags,
    user_settings,
    sharing_groups,
    authentication,
    users,
)

description = """
MISP API lets you use MISP as an API
"""

Base.metadata.create_all(bind=engine)

app = FastAPI()

# include Routes
app.include_router(attributes.router)
app.include_router(auth_key.router)
app.include_router(events.router)
app.include_router(user_settings.router)
app.include_router(feeds.router)
app.include_router(galaxies.router)
app.include_router(objects.router)
app.include_router(sightings.router)
app.include_router(tags.router)
app.include_router(sharing_groups.router)
app.include_router(users.router)
app.include_router(authentication.router)
