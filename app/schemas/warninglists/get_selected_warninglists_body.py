from pydantic import BaseModel


class GetSelectedWarninglistsBody(BaseModel):
    value: str
    enabled: bool
