import random
import string
import time

from mmisp.api_schemas.sightings.create_sighting_body import SightingCreateBody, SightingFiltersBody


def generate_random_value() -> str:
    octets = [str(random.randint(0, 255)) for _ in range(4)]
    return ".".join(octets)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_number_as_str() -> str:
    return str(random.randint(1, 100))


def random_bool() -> bool:
    return random.choice([True, False])


def random_list_of_strings() -> list[str]:
    return [random_string() for _ in range(random.randint(1, 5))]


def generate_random_filter() -> SightingFiltersBody:
    val = generate_random_value()
    return SightingFiltersBody(
        page=generate_number_as_str() if random_bool() else None,
        limit=generate_number_as_str() if random_bool() else None,
        value=val,
        value1=val,
        value2="",
        type=generate_number_as_str() if random_bool() else None,
        category=random_string() if random_bool() else None,
        org=random_string() if random_bool() else None,
        tags=random_list_of_strings() if random_bool() else None,
        from_=random_string() if random_bool() else None,
        to=random_string() if random_bool() else None,
        last=random_string() if random_bool() else None,
        event_id=generate_number_as_str(),
        with_attachments=random_bool(),
        uuid=random_string() if random_bool() else None,
        publish_timestamp=random_string() if random_bool() else None,
        published=random_bool(),
        timestamp=random_string() if random_bool() else None,
        attribute_timestamp=int(time.time()),
        enforce_warninglist=random_bool(),
        to_ids=random_bool(),
        deleted=random_bool(),
        event_timestamp=random_string() if random_bool() else None,
        threat_level_id=random_string() if random_bool() else None,
        eventinfo=random_string() if random_bool() else None,
        sharinggroup=random_list_of_strings() if random_bool() else None,
        decaying_model=random_string() if random_bool() else None,
        score=generate_number_as_str() if random_bool() else None,
        first_seen=random_string() if random_bool() else None,
        last_seen=random_string() if random_bool() else None,
        include_event_uuid=random_bool(),
        include_event_tags=random_bool(),
        include_proposals=random_bool(),
        requested_attributes=[generate_number_as_str() for _ in range(random.randint(1, 3))],
        include_context=random_bool(),
        headerless=random_bool(),
        include_warninglist_hits=random_bool(),
        attack_galaxy=random_string() if random_bool() else None,
        object_relation=random_string() if random_bool() else None,
        include_sightings=random_bool(),
        include_correlations=random_bool(),
        model_overrides=None,
        includeDecayScore=random_bool(),
        includeFullModel=random_bool(),
        excludeDecayed=random_bool(),
        returnFormat="json",
    )


def generate_valid_random_sighting_data() -> SightingCreateBody:
    return SightingCreateBody(
        values=[generate_random_value() for _ in range(random.randint(1, 2))],
        source=None,
        timestamp=int(time.time()),
        filters=generate_random_filter(),
    )
