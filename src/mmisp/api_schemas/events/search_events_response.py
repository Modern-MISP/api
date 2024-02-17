from pydantic import BaseModel

from .add_edit_get_event_response import AddEditGetEventResponse


class SearchEventsResponse(BaseModel):
    response: list[AddEditGetEventResponse]

    class Config:
        orm_mode = True
