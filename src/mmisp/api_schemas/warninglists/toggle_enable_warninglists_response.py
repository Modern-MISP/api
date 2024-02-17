from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str
    errors: str

    @validator("success", always=True)
    def check_status_false(cls, value: Any, values: Dict[str, Any]) -> Optional[str]:  # noqa: ANN101
        status = values.get("saved", None)
        if not status:
            return "[hidden]"
        return value

    @validator("errors")
    def check_status_true(cls, value: Any, values: Dict[str, Any]) -> Optional[str]:  # noqa: ANN101
        status = values.get("saved", None)
        if status:
            return "[hidden]"
        return value

    class Config:
        orm_mode = True
