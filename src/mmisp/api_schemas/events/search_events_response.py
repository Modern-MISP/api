from pydantic import BaseModel

from .add_edit_get_event_response import AddEditGetEventDetails


class SearchEventsResponse(BaseModel):
    response: list[AddEditGetEventDetails]

    class Config:
        orm_mode = True
