from pydantic import BaseModel


class CheckValueWarninglistsBody(BaseModel):
    value: list[str]
