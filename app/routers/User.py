from pydantic import BaseModel
from typing import List, Annotated


class User(BaseModel):
    id: str
    email: str
