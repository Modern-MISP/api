from pydantic import BaseModel


class DeleteSelectedAttributeBody(BaseModel):
    id: str  # id = "all" deletes all attributes in the event
    allow_hard_delete: bool | None = None

    class Config:
        orm_mode = True
