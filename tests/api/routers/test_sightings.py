import time
from typing import Any

import pytest

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.db.models.organisation import Organisation
from tests.environment import client, environment, get_db
from tests.generators.sighting_generator import (
    generate_valid_random_sighting_data,
)


@pytest.fixture(
    params=[
        generate_valid_random_sighting_data().dict(),
    ]
)
def feed_data(request: Any) -> dict[str, Any]:
    return request.param


class TestAddSighting:
    def test_add_sighting(self: "TestAddSighting", feed_data: dict[str, Any]) -> None:
        db = get_db()

        organisation = Organisation(
            name="test",
            date_created=str(int(time.time())),
            date_modified=str(int(time.time())),
        )
        db.add(organisation)
        db.flush()
        db.refresh(organisation)

        event = Event(
            org_id=organisation.id,
            orgc_id=organisation.id,
            info="test",
            date=str(int(time.time())),
            analysis="test",
            event_creator_email="XXXXXXXXXXXXX",
        )
        db.add(event)
        db.flush()
        db.refresh(event)

        for val in feed_data["values"]:
            attributes = Attribute(
                event_id=event.id,
                category="test",
                type="test",
                value=val,
            )

            db.add(attributes)

        db.commit()

        headers = {"authorization": environment.site_admin_user_token}
        response = client.post("/feeds", json=feed_data, headers=headers)

        assert response.status_code == 201
