from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel


class Galaxies(BaseModel):
    id: str = ""
    uuid: str = ""
    name: str = ""
    type: str = ""
    description: str = ""
    version: str = ""
    icon: str = ""
    namespace: str = ""
    kill_chain_order: List[str] = [""]


app = FastAPI()
