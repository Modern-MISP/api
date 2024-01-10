from pydantic import Field, BaseModel

class UpdateNoticelist(BaseModel):
    saved: bool
    success: bool
    name: str
    message: str
    url: str