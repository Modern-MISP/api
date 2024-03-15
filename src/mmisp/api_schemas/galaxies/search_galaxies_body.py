from pydantic import BaseModel


class SearchGalaxiesbyValue(BaseModel):
    value: str


class SearchGalaxiesBody(BaseModel):
    id: str | None = None
    uuid: str | None = None
    name: str | None = None
    type: str | None = None
    description: str | None = None
    version: str | None = None
    icon: str | None = None
    namespace: str | None = None
    kill_chain_order: str | None = None
    enabled: bool | None = None
    local_only: bool | None = None

    class Config:
        orm_mode = True
