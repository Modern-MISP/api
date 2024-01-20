from pydantic import BaseModel


class DeleteSelectedAttributeBody(BaseModel):
    id: str  # mandatory (id = "all" deletes all attributes in the event)
    event_id: str  # mandatory
    allow_hard_delete: bool  # optional

    class Config:
        orm_mode = True
