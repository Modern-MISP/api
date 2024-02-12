from mmisp.api_schemas.events.add_event_body import AddEventBody


def generate_valid_add_event_body() -> AddEventBody:
    return AddEventBody(info="test event")
