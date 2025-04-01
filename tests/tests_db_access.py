import pytest
from icecream import ic
from sqlalchemy import select
from sqlalchemy.sql.expression import false

from mmisp.db.models.attribute import Attribute
from mmisp.db.models.event import Event
from mmisp.tests.maps import (
    user_to_attributes,
)

all_users = [
    "user_org1_publisher",
    "user_org1_read_only",
    "user_org1_user",
    "user_org2_publisher",
    "user_org2_read_only",
    "user_org2_user",
    "site_admin_user",
]


@pytest.mark.parametrize("user_key", all_users)
@pytest.mark.asyncio
async def test_event_access(db, access_test_objects, user_key) -> None:
    user = access_test_objects[user_key]
    await db.refresh(access_test_objects["org1"])
    await db.refresh(access_test_objects["org2"])
    await db.refresh(access_test_objects["org3"])

    result = await db.execute(select(Event))
    all_events = result.scalars().all()
    ic(len(all_events))

    result = await db.execute(select(Event).filter(Event.can_access(user)))
    can_access_events = result.scalars().all()

    for event in can_access_events:
        assert event.can_access(user)

    result = await db.execute(select(Event).filter(Event.can_access(user) == false()))
    can_not_access_events = result.scalars().all()

    for event in can_not_access_events:
        assert not event.can_access(user)

    assert len(can_access_events) + len(can_not_access_events) == len(all_events)


@pytest.mark.parametrize("user_key", all_users)
@pytest.mark.asyncio
async def test_attribute_access(db, access_test_objects, user_key) -> None:
    user = access_test_objects[user_key]
    await db.refresh(access_test_objects["org1"])
    await db.refresh(access_test_objects["org2"])
    await db.refresh(access_test_objects["org3"])

    result = await db.execute(select(Attribute))
    all_attributes = result.scalars().all()
    ic(len(all_attributes))

    result = await db.execute(select(Attribute).filter(Attribute.can_access(user)))
    can_access_attributes = result.scalars().all()
    ic(len(can_access_attributes))

    list_of_attributes = None
    for user_str, attribute_list in user_to_attributes:
        if user_str == user_key:
            list_of_attributes = attribute_list
            break

    for attribute in can_access_attributes:
        assert attribute.value in list_of_attributes
        assert attribute.can_access(user)

    result = await db.execute(select(Attribute).filter(Attribute.can_access(user) == false()))
    can_not_access_attributes = result.scalars().all()
    ic(len(can_not_access_attributes))

    for attribute in can_not_access_attributes:
        assert not attribute.can_access(user)

    assert len(can_access_attributes) + len(can_not_access_attributes) == len(all_attributes)


async def test_time(access_test_objects) -> None:
    assert False


async def test_time2(access_test_objects) -> None:
    assert False
