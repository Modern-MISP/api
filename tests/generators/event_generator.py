from random import randint
from typing import Any, Dict

from mmisp.api_schemas.events.add_event_body import AddEventBody
from mmisp.api_schemas.events.edit_event_body import EditEventBody


def generate_valid_add_event_body() -> AddEventBody:
    return AddEventBody(info="test event")


def generate_invalid_add_event_body() -> AddEventBody:
    return AddEventBody(info=10)


def generate_non_existing_id() -> str:
    return "0"


def generate_invalid_id() -> str:
    return "invalid id"


def generate_valid_update_event_body() -> EditEventBody:
    return EditEventBody(info="updated info")


def generate_invalid_update_event_body() -> EditEventBody:
    return EditEventBody(info=False)


def generate_valid_local_add_tag_to_event() -> str:
    return str(randint(0, 1))


def generate_valid_add_attribute_via_free_text_import_body() -> Dict[str, Any]:
    return {"Attribute": {"value": "1.2.3.4 test_value"}}
