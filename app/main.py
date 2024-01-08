from typing import Union

from fastapi import FastAPI

from .database import engine
from .models.feed import Base
from .routers import auth_key, feeds, objects, sightings, tags, user_settings

description = """
MISP API lets you use MISP as an API
"""

Base.metadata.create_all(bind=engine)

app = FastAPI()

# include Routes
# app.include_router(attributes.router)
app.include_router(auth_key.router)
app.include_router(user_settings.router)
app.include_router(feeds.router)
app.include_router(objects.router)
app.include_router(sightings.router)
app.include_router(tags.router)


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict:
    return {"item_id": item_id, "q": q}
