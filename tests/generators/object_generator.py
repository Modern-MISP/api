import random
import string
import time

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.search_objects_body import ObjectModelSearchOverridesBody, ObjectSearchBody


def generate_random_date_str() -> str:
    return str(int(time.time()))


def generate_number_as_str() -> str:
    number = random.randint(1, 4)
    return str(number)


def generate_ids_as_str() -> str:
    id_str = random.randint(1, 100)
    return str(id_str)


def generate_random_str(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Generate object data
def generate_valid_object_create_attributes() -> AddAttributeBody:
    return AddAttributeBody(
        type=generate_random_str(),
        value=generate_random_str(),
        value1=generate_random_str(),
        value2=generate_random_str(),
        event_id=generate_ids_as_str(),
        category=generate_random_str(),
        to_ids=random.choice([True, False]),
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
        action=generate_random_str(),
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
        attributes=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
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
        to_ids=random.choice([True, False]),
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
        action=generate_random_str(),
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
        attributes=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
    )


# Generate search data
def generate_random_model_overrides() -> ObjectModelSearchOverridesBody:
    return ObjectModelSearchOverridesBody(
        lifetime=random.randint(1, 100),
        decay_speed=random.uniform(0.1, 1.0),
        threshold=random.randint(1, 100),
        default_base_score=random.randint(1, 100),
        base_score_config={generate_random_str(5): random.uniform(0.1, 1.0) for _ in range(3)},
    )


def generate_specific_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        eventid="1",
        to_ids=random.choice([True, False]),
    )


def generate_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        page=random.randint(1, 10),
        limit=random.randint(1, 100),
        quickFilter=generate_random_str(),
        searchall=generate_random_str(),
        timestamp=generate_random_date_str(),
        object_name=generate_random_str(),
        object_template_uuid=generate_random_str(32),
        object_template_version=generate_random_str(),
        eventid=str(random.randint(1, 10000)),
        eventinfo=generate_random_str(),
        ignore=random.choice([True, False]),
        from_=generate_random_date_str(),
        to=generate_random_date_str(),
        date=generate_random_date_str(),
        tags=[generate_random_str() for _ in range(3)],
        last=random.randint(1, 365),
        event_timestamp=generate_random_date_str(),
        publish_timestamp=generate_random_date_str(),
        org=generate_random_str(),
        uuid=generate_random_str(32),
        value1=generate_random_str(),
        value2=generate_random_str(),
        type=generate_random_str(),
        category=generate_random_str(),
        object_relation=generate_random_str(),
        attribute_timestamp=generate_random_date_str(),
        first_seen=generate_random_date_str(),
        last_seen=generate_random_date_str(),
        comment=generate_random_str(),
        to_ids=random.choice([True, False]),
        published=random.choice([True, False]),
        deleted=random.choice([True, False]),
        withAttachments=random.choice([True, False]),
        enforceWarninglist=random.choice([True, False]),
        includeAllTags=random.choice([True, False]),
        includeEventUuid=random.choice([True, False]),
        include_event_uuid=random.choice([True, False]),
        includeEventTags=random.choice([True, False]),
        includeProposals=random.choice([True, False]),
        includeWarninglistHits=random.choice([True, False]),
        includeContext=random.choice([True, False]),
        includeSightings=random.choice([True, False]),
        includeSightingdb=random.choice([True, False]),
        includeCorrelations=random.choice([True, False]),
        includeDecayScore=random.choice([True, False]),
        includeFullModel=random.choice([True, False]),
        allow_proposal_blocking=random.choice([True, False]),
        metadata=random.choice([True, False]),
        attackGalaxy=generate_random_str(),
        excludeDecayed=random.choice([True, False]),
        decayingModel=generate_random_str(),
        modelOverrides=generate_random_model_overrides(),
        score=generate_random_str(),
        # returnFormat=["json"],  #? default should be json
        # returnFormat=random.choice(['json', 'xml', 'csv'])
    )


# Generate random search data
def generate_random_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        page=random.randint(1, 10) if random.choice([True, False]) else None,
        limit=random.randint(1, 100) if random.choice([True, False]) else None,
        quickFilter=generate_random_str() if random.choice([True, False]) else None,
        searchall=generate_random_str() if random.choice([True, False]) else None,
        timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        object_name=generate_random_str() if random.choice([True, False]) else None,
        object_template_uuid=generate_random_str(32) if random.choice([True, False]) else None,
        object_template_version=generate_random_str() if random.choice([True, False]) else None,
        eventid=str(random.randint(1, 10000)) if random.choice([True, False]) else None,
        eventinfo=generate_random_str() if random.choice([True, False]) else None,
        ignore=random.choice([True, False]) if random.choice([True, False]) else None,
        from_=generate_random_date_str() if random.choice([True, False]) else None,
        to=generate_random_date_str() if random.choice([True, False]) else None,
        date=generate_random_date_str() if random.choice([True, False]) else None,
        tags=[generate_random_str() for _ in range(3)] if random.choice([True, False]) else None,
        last=random.randint(1, 365) if random.choice([True, False]) else None,
        event_timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        publish_timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        org=generate_random_str() if random.choice([True, False]) else None,
        uuid=generate_random_str(32) if random.choice([True, False]) else None,
        value1=generate_random_str() if random.choice([True, False]) else None,
        value2=generate_random_str() if random.choice([True, False]) else None,
        type=generate_random_str() if random.choice([True, False]) else None,
        category=generate_random_str() if random.choice([True, False]) else None,
        object_relation=generate_random_str() if random.choice([True, False]) else None,
        attribute_timestamp=generate_random_date_str() if random.choice([True, False]) else None,
        first_seen=generate_random_date_str() if random.choice([True, False]) else None,
        last_seen=generate_random_date_str() if random.choice([True, False]) else None,
        comment=generate_random_str() if random.choice([True, False]) else None,
        to_ids=random.choice([True, False]) if random.choice([True, False]) else None,
        published=random.choice([True, False]) if random.choice([True, False]) else None,
        deleted=random.choice([True, False]) if random.choice([True, False]) else None,
        withAttachments=random.choice([True, False]) if random.choice([True, False]) else None,
        enforceWarninglist=random.choice([True, False]) if random.choice([True, False]) else None,
        includeAllTags=random.choice([True, False]) if random.choice([True, False]) else None,
        includeEventUuid=random.choice([True, False]) if random.choice([True, False]) else None,
        include_event_uuid=random.choice([True, False]) if random.choice([True, False]) else None,
        includeEventTags=random.choice([True, False]) if random.choice([True, False]) else None,
        includeProposals=random.choice([True, False]) if random.choice([True, False]) else None,
        includeWarninglistHits=random.choice([True, False]) if random.choice([True, False]) else None,
        includeContext=random.choice([True, False]) if random.choice([True, False]) else None,
        includeSightings=random.choice([True, False]) if random.choice([True, False]) else None,
        includeSightingdb=random.choice([True, False]) if random.choice([True, False]) else None,
        includeCorrelations=random.choice([True, False]) if random.choice([True, False]) else None,
        includeDecayScore=random.choice([True, False]) if random.choice([True, False]) else None,
        includeFullModel=random.choice([True, False]) if random.choice([True, False]) else None,
        allow_proposal_blocking=random.choice([True, False]) if random.choice([True, False]) else None,
        metadata=random.choice([True, False]) if random.choice([True, False]) else None,
        attackGalaxy=generate_random_str() if random.choice([True, False]) else None,
        excludeDecayed=random.choice([True, False]) if random.choice([True, False]) else None,
        decayingModel=generate_random_str() if random.choice([True, False]) else None,
        modelOverrides=generate_random_model_overrides() if random.choice([True, False]) else None,
        score=generate_random_str() if random.choice([True, False]) else None,
        # returnFormat=["json"],  #? default should be json
        # returnFormat=random.choice(['json', 'xml', 'csv'])
    )
