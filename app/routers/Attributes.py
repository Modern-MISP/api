from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel


class Attributes(BaseModel):
    id: str = ""
    event_id: str = ""
    object_id: str = ""
    object_relation: str = ""
    category: str = ""
    type: str = ""
    value: str = ""
    to_ids: bool = True
    uuid: str = ""
    timestamp: str = ""
    distribution: str = ""
    sharing_group_id: str = ""
    comment: str = ""
    deleted: bool = False
    disable_correlation: bool = False
    first_seen: str = ""
    last_seen: str = ""


app = FastAPI()
