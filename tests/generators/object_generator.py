import random
import string
import time

from mmisp.api_schemas.attributes import AddAttributeBody
from mmisp.api_schemas.objects import ObjectCreateBody, ObjectSearchBody


def generate_random_date_str() -> str:
    return str(int(time.time()))


def generate_random_value() -> str:
    octets = [str(random.randint(0, 255)) for _ in range(4)]
    return ".".join(octets)


def generate_number_as_str() -> str:
    number = random.randint(1, 4)
    return str(number)


def generate_ids_as_str() -> str:
    id_str = random.randint(1, 50)
    return str(id_str)


def generate_random_str(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Generate object data
def generate_valid_object_create_attributes() -> AddAttributeBody:
    return AddAttributeBody(
        type="text",
        value=generate_random_str(),
        event_id=generate_ids_as_str(),
        category=generate_random_str(),
        to_ids=True,
        timestamp=generate_random_date_str(),
        distribution=generate_number_as_str(),
        sharing_group_id=generate_ids_as_str(),
        comment=generate_random_str(),
        deleted=False,
        disable_correlation=random.choice([True, False]),
    )


def generate_valid_object_data() -> ObjectCreateBody:
    return ObjectCreateBody(
        name=generate_random_str(),
        meta_category=generate_random_str(),
        description=generate_random_str(),
        template_version="100",
        timestamp=generate_random_date_str(),
        distribution=generate_number_as_str(),
        sharing_group_id=generate_ids_as_str(),
        comment=generate_random_str(),
        deleted=False,
        first_seen=generate_random_date_str(),
        last_seen=generate_random_date_str(),
        Attribute=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
    )


# Generate random object data
def generate_valid_random_object_create_attributes() -> AddAttributeBody:
    return AddAttributeBody(
        type=generate_random_str(),
        value=generate_random_str(),
        value1=generate_random_str(),
        value2=generate_random_str(),
        event_id=generate_ids_as_str(),
        category=generate_random_str(),
        to_ids=True,
        timestamp=generate_random_date_str(),
        distribution=generate_number_as_str(),
        sharing_group_id=generate_ids_as_str(),
        comment=generate_random_str(),
        deleted=False,
        disable_correlation=random.choice([True, False]),
    )


def generate_valid_random_object_data() -> ObjectCreateBody:
    return ObjectCreateBody(
        name=generate_random_str(),
        meta_category=generate_random_str(),
        description=generate_random_str(),
        template_name=generate_random_str(),
        template_version="100",
        template_description=generate_random_str(),
        update_template_available=random.choice([True, False]),
        timestamp=generate_random_date_str(),
        distribution=generate_number_as_str(),
        sharing_group_id=generate_ids_as_str(),
        comment=generate_random_str(),
        deleted=False,
        first_seen=generate_random_date_str(),
        last_seen=generate_random_date_str(),
        Attribute=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
    )


# Generate search data
def generate_specific_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        value=generate_random_str(),
        value1=generate_random_value(),
        eventid="1",
        to_ids=True,
        limit="50",
    )


def generate_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        object_name=generate_random_str(),
        object_template_uuid=generate_random_str(),
        object_template_version=generate_ids_as_str(),
        event_id=generate_ids_as_str(),
        category=generate_random_str(),
        comment=generate_random_str(),
        first_seen=generate_random_date_str(),
        last_seen=generate_random_date_str(),
        quickFilter=generate_random_str(),
        timestamp=generate_random_date_str(),
        event_info=generate_random_str(),
        from_=generate_random_date_str(),
        to=generate_random_date_str(),
        date="2024-02-17",
        last=generate_random_date_str(),
        event_timestamp=generate_random_date_str(),
        org_id=generate_ids_as_str(),
        uuid=generate_random_str(),
        value=generate_random_str(),
        value1=generate_random_value(),
        value2="",
        type=generate_random_str(),
        attribute_timestamp=generate_random_date_str(),
        to_ids=True,
        published=random.choice([True, False]),
        deleted=random.choice([True, False]),
        returnFormat="json",
        limit="10",
    )


# Generate random search data
def generate_random_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        object_name=generate_random_str() if random.choice([True, False]) else None,
        object_template_uuid=generate_random_str() if random.choice([True, False]) else None,
        object_template_version=generate_ids_as_str() if random.choice([True, False]) else None,
        event_id=generate_ids_as_str(),
        category=generate_random_str() if random.choice([True, False]) else None,
        comment=generate_random_str(),
        first_seen=generate_random_date_str() if random.choice([True, False]) else None,
        last_seen=generate_random_date_str() if random.choice([True, False]) else None,
        quickFilter=generate_random_str() if random.choice([True, False]) else None,
        timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        event_info=generate_random_str() if random.choice([True, False]) else None,
        from_=generate_random_date_str() if random.choice([True, False]) else None,
        to=generate_random_date_str() if random.choice([True, False]) else None,
        date="2024-02-17" if random.choice([True, False]) else None,
        last=generate_random_date_str() if random.choice([True, False]) else None,
        event_timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        org_id=generate_ids_as_str() if random.choice([True, False]) else None,
        uuid=generate_random_str() if random.choice([True, False]) else None,
        value=generate_random_str(),
        value1=generate_random_value() if random.choice([True, False]) else None,
        value2="" if random.choice([True, False]) else None,
        type=generate_random_str() if random.choice([True, False]) else None,
        attribute_timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        to_ids=True,
        published=random.choice([True, False]) if random.choice([True, False]) else None,
        deleted=random.choice([True, False]) if random.choice([True, False]) else None,
        returnFormat="json",
        limit="10" if random.choice([True, False]) else None,
    )
