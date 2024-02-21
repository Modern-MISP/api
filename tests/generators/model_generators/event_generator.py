import datetime

from mmisp.db.models.event import Event


def generate_event() -> Event:
    return Event(
        org_id=1,
        orgc_id=1,
        info="test event",
        date=datetime.date(year=2024, month=2, day=13),
        analysis="test analysis",
        event_creator_email="test@mail.de",
    )
