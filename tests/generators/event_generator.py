from mmisp.api_schemas.events.add_event_body import AddEventBody


def generate_valid_add_event_body() -> AddEventBody:
    return AddEventBody(info="test event")


def generate_invalid_add_event_body() -> AddEventBody:
    return AddEventBody(info=10)


def generate_non_existing_id() -> str:
    return "0"


def generate_invalid_id() -> str:
    return "invalid id"
