from pydantic import BaseModel


class DeleteAttributeResponse(BaseModel):
    message: str

    class Config:
        orm_mode = True
