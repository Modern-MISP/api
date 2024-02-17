from mmisp.api_schemas.standard_status_response import StandardStatusResponse


class ToggleEnableNoticelist(StandardStatusResponse):
    id: str

    class Config:
        orm_mode = True
