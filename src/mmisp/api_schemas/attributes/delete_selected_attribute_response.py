from pydantic import BaseModel


class DeleteSelectedAttributeResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: list[str]

    class Config:
        orm_mode = True
