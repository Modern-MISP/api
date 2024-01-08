from typing import List

from pydantic import BaseModel


class GalaxySchema(BaseModel):
    id: str
    uuid: str
    name: str
    type: str
    description: str
    version: str
    icon: str
    namespace: str
    kill_chain_order: List[str]

    class Config:
        orm_mode = True
