from typing import List, Union

import User
from fastapi import FastAPI
from pydantic import BaseModel


class AuthKey(BaseModel):
    id: str = ""
    uuid: str = ""
    authkey_start: str = ""
    authkey_end: str = ""
    created: str = ""
    expiration: str = ""
    read_only: bool = False
    user_id: str = ""
    comment: str = ""
    allowed_ips: str = ""  # Stringified JSON Array of IP addresses
    last_used: str = ""
    unique_ips: List[str] = [""]
    authkey_raw: str = ""


app = FastAPI()


@app.get("/auth_keys/")
async def auth_keys_get() -> Union[AuthKey, User.User]:  # Request Body in die Klammern
    return {AuthKey(), User.User()}  # return body in nach return


@app.post("/auth_keys/")
async def auth_keys_post(authkey: AuthKey) -> Union[AuthKey, User.User]:
    return {{AuthKey(), User.User()}}


@app.post("/auth_keys/add/{UserId")
async def auth_keys_add_User(UserId: str, authKey: AuthKey) -> AuthKey:
    return AuthKey()
