from pydantic import BaseModel


class AttributeDeleteSelectedBody(BaseModel):
    id: str  # mandatory
    event_id: str  # mandatory
    allow_hard_delete: bool  # optional

    class Config:
        orm_mode = True