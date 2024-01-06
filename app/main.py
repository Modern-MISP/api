from typing import Union

from fastapi import FastAPI
from routers import AuthKey, UserSettings  # , Attributes

description = """
MISP API lets you use MISP as an API
"""

app = FastAPI()

# include Routes
# app.include_router(Attributes.router)
app.include_router(AuthKey.router)
app.include_router(UserSettings.router)


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict:
    return {"item_id": item_id, "q": q}
