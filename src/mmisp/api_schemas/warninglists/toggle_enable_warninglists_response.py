from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


class ToggleEnableWarninglistsResponse(BaseModel):
    saved: bool
    success: str
    errors: str

    @validator("success", always=True)
    def check_status_false(cls, value: Any, values: Dict[str, Any]) -> Optional[str]:  # noqa: ANN101
        status = values.get("saved")
        if status is False:
            return "[hidden]"
        return value

    @validator("errors")
    def check_status_true(cls, value: Any, values: Dict[str, Any]) -> Optional[str]:  # noqa: ANN101
        status = values.get("saved")
        if status is True:
            return "[hidden]"
        return value

    class Config:
        orm_mode = True
