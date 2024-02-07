import random
import string

from src.mmisp.api_schemas.feeds.create_update_feed_body import FeedCreateAndUpdateBody


def generate_number() -> int:
    number = random.randint(1, 4)
    return number


def generate_ids_as_str() -> str:
    id_str = random.randint(1, 10)
    return str(id_str)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_valid_required_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
    )


def generate_valid_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        rules=random_string(),
        enabled=False,
        distribution=generate_number(),
        sharing_group_id=generate_ids_as_str(),
        tag_id=generate_ids_as_str(),
        default=random.choice([True, False]),
        source_format=random_string(),
        fixed_event=random.choice([True, False]),
        delta_merge=random.choice([True, False]),
        event_id=generate_ids_as_str(),
        publish=random.choice([True, False]),
        override_ids=random.choice([True, False]),
        settings=random_string(),
        input_source=random_string(),
        delete_local_file=random.choice([True, False]),
        lookup_visible=random.choice([True, False]),
        headers=random_string(),
        caching_enabled=random.choice([True, False]),
        force_to_ids=random.choice([True, False]),
        orgc_id=generate_ids_as_str(),
    )


def generate_random_valid_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        rules=random_string() if random.choice([True, False]) else None,
        enabled=None,
        distribution=generate_number() if random.choice([True, False]) else None,
        sharing_group_id=generate_ids_as_str() if random.choice([True, False]) else None,
        tag_id=generate_ids_as_str() if random.choice([True, False]) else None,
        default=random.choice([True, False]) if random.choice([True, False]) else None,
        source_format=random_string() if random.choice([True, False]) else None,
        fixed_event=random.choice([True, False]) if random.choice([True, False]) else None,
        delta_merge=random.choice([True, False]) if random.choice([True, False]) else None,
        event_id=generate_ids_as_str() if random.choice([True, False]) else None,
        publish=random.choice([True, False]) if random.choice([True, False]) else None,
        override_ids=random.choice([True, False]) if random.choice([True, False]) else None,
        settings=random_string() if random.choice([True, False]) else None,
        input_source=random_string() if random.choice([True, False]) else None,
        delete_local_file=random.choice([True, False]) if random.choice([True, False]) else None,
        lookup_visible=random.choice([True, False]) if random.choice([True, False]) else None,
        headers=random_string() if random.choice([True, False]) else None,
        caching_enabled=random.choice([True, False]) if random.choice([True, False]) else None,
        force_to_ids=random.choice([True, False]) if random.choice([True, False]) else None,
        orgc_id=generate_ids_as_str() if random.choice([True, False]) else None,
    )
