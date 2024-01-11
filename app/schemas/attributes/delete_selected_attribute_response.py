from pydantic import BaseModel


class DeleteSelectedAttributeResponse(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str
    id: str

    class Config:
        orm_mode = True
