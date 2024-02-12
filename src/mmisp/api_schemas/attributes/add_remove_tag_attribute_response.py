from typing import Optional

from pydantic import BaseModel


class AddRemoveTagAttributeResponse(BaseModel):
    saved: bool
    success: Optional[str]
    check_publish: Optional[bool]
    errors: Optional[str]

    class Config:
        orm_mode = True
