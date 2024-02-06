import random
import string

from src.mmisp.api_schemas.feeds.create_update_feed_body import FeedCreateAndUpdateBody


def generate_number_string() -> str:
    number = random.randint(1, 4)
    return str(number)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_valid_required_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        enabled="False",
        distribution=generate_number_string(),
        source_format=random_string(),
        fixed_event=str(random.choice([True, False])),
    )


def generate_valid_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        rules=random_string(),
        enabled="False",
        distribution=generate_number_string(),
        sharing_group_id=generate_number_string(),
        tag_id=generate_number_string(),
        source_format=random_string(),
        fixed_event=str(random.choice([True, False])),
        delta_merge=random.choice([True, False]),
        event_id=generate_number_string(),
        publish=random.choice([True, False]),
        override_ids=random.choice([True, False]),
        input_source=random_string(),
        delete_local_file=random.choice([True, False]),
        lookup_visible=random.choice([True, False]),
        headers=random_string(),
        caching_enabled=random.choice([True, False]),
        force_to_ids=random.choice([True, False]),
        orgc_id=generate_number_string(),
    )


def generate_random_valid_feed_data() -> FeedCreateAndUpdateBody:
    return FeedCreateAndUpdateBody(
        name=random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        rules=random_string() if random.choice([True, False]) else None,
        enabled="False",
        distribution=generate_number_string(),
        sharing_group_id=generate_number_string() if random.choice([True, False]) else None,
        tag_id=generate_number_string() if random.choice([True, False]) else None,
        source_format=random_string(),
        fixed_event=str(random.choice([True, False])),
        delta_merge=random.choice([True, False]) if random.choice([True, False]) else None,
        event_id=generate_number_string() if random.choice([True, False]) else None,
        publish=random.choice([True, False]) if random.choice([True, False]) else None,
        override_ids=random.choice([True, False]) if random.choice([True, False]) else None,
        input_source=random_string() if random.choice([True, False]) else None,
        delete_local_file=random.choice([True, False]) if random.choice([True, False]) else None,
        lookup_visible=random.choice([True, False]) if random.choice([True, False]) else None,
        headers=random_string() if random.choice([True, False]) else None,
        caching_enabled=random.choice([True, False]) if random.choice([True, False]) else None,
        force_to_ids=random.choice([True, False]) if random.choice([True, False]) else None,
        orgc_id=generate_number_string() if random.choice([True, False]) else None,
    )
