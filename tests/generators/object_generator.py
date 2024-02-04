import random
import string
from datetime import datetime, timedelta

from mmisp.api_schemas.attributes.add_attribute_body import AddAttributeBody
from mmisp.api_schemas.objects.create_object_body import ObjectCreateBody
from mmisp.api_schemas.objects.search_objects_body import ObjectModelSearchOverridesBody, ObjectSearchBody


def random_date_string() -> str:
    random_date = datetime.now() - timedelta(days=random.randint(0, 365))
    return random_date.strftime("%Y-%m-%d")


def generate_number() -> int:
    return random.randint(1, 100)


def generate_random_big_integer() -> str:
    max_int_64 = 2**63 - 1
    return str(random.randint(0, max_int_64))


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_valid_object_create_attributes() -> AddAttributeBody:
    return AddAttributeBody(
        type=random_string(),
        category=random_string(),
        value=random_string(),
        value1=random_string(),
        value2=random_string(),
        to_ids=random.choice([True, False]),
        disable_correlation=random.choice([True, False]),
        distribution=str(1 if random.choice([True, False]) else 0),
        comment=random_string(),
    )


# def generate_valid_req_data() -> ObjectCreateRequirementBody:
#     return ObjectCreateRequirementBody(requirement=random_string(), requirement_type=random_string)


# Generate object data
def generate_valid_object_data() -> ObjectCreateBody:
    return ObjectCreateBody(
        name=random_string(),
        description=random_string(),
        update_template_available=random.choice([True, False]),
        action=random_string(),
        template_name=random_string(),
        template_version=random_string(),
        template_description=random_string(),
        # requirements={random_string(): random_string()},
        meta_category=random_string(),
        distribution=str(1 if random.choice([True, False]) else 0),
        sharing_group_id=generate_number(),
        comment=random_string(),
        first_seen=generate_random_big_integer(),
        last_seen=generate_random_big_integer(),
        attributes=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
    )


def generate_valid_random_object_create_attributes() -> AddAttributeBody:
    return AddAttributeBody(
        type=random_string(),
        category=random_string(),
        value=random_string(),
        value1=random_string() if random.choice([True, False]) else None,
        value2=random_string() if random.choice([True, False]) else None,
        to_ids=random.choice([True, False]),
        disable_correlation=random.choice([True, False]),
        distribution=str(1 if random.choice([True, False]) else 0),
        comment=random_string() if random.choice([True, False]) else None,
    )


# Generate random object data
def generate_valid_random_object_data() -> ObjectCreateBody:
    return ObjectCreateBody(
        name=random_string(),
        description=random_string(),
        update_template_available=random.choice([True, False]) if random.choice([True, False]) else None,
        action=random_string() if random.choice([True, False]) else None,
        template_name=random_string() if random.choice([True, False]) else None,
        template_version=random_string() if random.choice([True, False]) else None,
        template_description=random_string() if random.choice([True, False]) else None,
        # requirements=generate_valid_req_data().dict() if random.choice([True, False]) else None,
        meta_category=random_string(),
        distribution=str(1 if random.choice([True, False]) else 0),
        sharing_group_id=generate_number() if random.choice([True, False]) else None,
        comment=random_string() if random.choice([True, False]) else None,
        first_seen=generate_random_big_integer() if random.choice([True, False]) else None,
        last_seen=generate_random_big_integer() if random.choice([True, False]) else None,
        attributes=[generate_valid_object_create_attributes() for _ in range(random.randint(1, 5))],
    )


# Generate search data
def generate_random_model_overrides() -> ObjectModelSearchOverridesBody:
    return ObjectModelSearchOverridesBody(
        lifetime=random.randint(1, 100),
        decay_speed=random.uniform(0.1, 1.0),
        threshold=random.randint(1, 100),
        default_base_score=random.randint(1, 100),
        base_score_config={random_string(5): random.uniform(0.1, 1.0) for _ in range(3)},
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
        quickFilter=random_string(),
        searchall=random_string(),
        timestamp=random_date_string(),
        object_name=random_string(),
        object_template_uuid=random_string(32),
        object_template_version=random_string(),
        eventid=str(random.randint(1, 10000)),
        eventinfo=random_string(),
        ignore=random.choice([True, False]),
        from_=random_date_string(),
        to=random_date_string(),
        date=random_date_string(),
        tags=[random_string() for _ in range(3)],
        last=random.randint(1, 365),
        event_timestamp=random_date_string(),
        publish_timestamp=random_date_string(),
        org=random_string(),
        uuid=random_string(32),
        value1=random_string(),
        value2=random_string(),
        type=random_string(),
        category=random_string(),
        object_relation=random_string(),
        attribute_timestamp=random_date_string(),
        first_seen=random_date_string(),
        last_seen=random_date_string(),
        comment=random_string(),
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
        attackGalaxy=random_string(),
        excludeDecayed=random.choice([True, False]),
        decayingModel=random_string(),
        modelOverrides=generate_random_model_overrides(),
        score=random_string(),
        # returnFormat=["json"],  #? default should be json
        # returnFormat=random.choice(['json', 'xml', 'csv'])
    )


def generate_random_search_query() -> ObjectSearchBody:
    return ObjectSearchBody(
        page=random.randint(1, 10) if random.choice([True, False]) else None,
        limit=random.randint(1, 100) if random.choice([True, False]) else None,
        quickFilter=random_string() if random.choice([True, False]) else None,
        searchall=random_string() if random.choice([True, False]) else None,
        timestamp=random_date_string() if random.choice([True, False]) else None,
        object_name=random_string() if random.choice([True, False]) else None,
        object_template_uuid=random_string(32) if random.choice([True, False]) else None,
        object_template_version=random_string() if random.choice([True, False]) else None,
        eventid=str(random.randint(1, 10000)) if random.choice([True, False]) else None,
        eventinfo=random_string() if random.choice([True, False]) else None,
        ignore=random.choice([True, False]) if random.choice([True, False]) else None,
        from_=random_date_string() if random.choice([True, False]) else None,
        to=random_date_string() if random.choice([True, False]) else None,
        date=random_date_string() if random.choice([True, False]) else None,
        tags=[random_string() for _ in range(3)] if random.choice([True, False]) else None,
        last=random.randint(1, 365) if random.choice([True, False]) else None,
        event_timestamp=random_date_string() if random.choice([True, False]) else None,
        publish_timestamp=random_date_string() if random.choice([True, False]) else None,
        org=random_string() if random.choice([True, False]) else None,
        uuid=random_string(32) if random.choice([True, False]) else None,
        value1=random_string() if random.choice([True, False]) else None,
        value2=random_string() if random.choice([True, False]) else None,
        type=random_string() if random.choice([True, False]) else None,
        category=random_string() if random.choice([True, False]) else None,
        object_relation=random_string() if random.choice([True, False]) else None,
        attribute_timestamp=random_date_string() if random.choice([True, False]) else None,
        first_seen=random_date_string() if random.choice([True, False]) else None,
        last_seen=random_date_string() if random.choice([True, False]) else None,
        comment=random_string() if random.choice([True, False]) else None,
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
        attackGalaxy=random_string() if random.choice([True, False]) else None,
        excludeDecayed=random.choice([True, False]) if random.choice([True, False]) else None,
        decayingModel=random_string() if random.choice([True, False]) else None,
        modelOverrides=generate_random_model_overrides() if random.choice([True, False]) else None,
        score=random_string() if random.choice([True, False]) else None,
        # returnFormat=["json"],  #? default should be json
        # returnFormat=random.choice(['json', 'xml', 'csv'])
    )
