import random
import string
import time

from mmisp.api_schemas.sightings import SightingCreateBody, SightingFiltersBody


def generate_random_value() -> str:
    octets = [str(random.randint(0, 255)) for _ in range(4)]
    return ".".join(octets)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_number_as_str() -> str:
    return str(random.randint(1, 100))


def random_list_of_strings() -> list[str]:
    return [random_string() for _ in range(random.randint(1, 5))]


def generate_valid_random_sighting_data() -> SightingCreateBody:
    return SightingCreateBody(
        values=[generate_random_value() for _ in range(random.randint(1, 2))],
        source=None,
        timestamp=int(time.time()),
        filters=None,
    )


def generate_random_search_query() -> SightingFiltersBody:
    return SightingFiltersBody(
        value1=None,  # Fields are set in the test
        value2="",
    )


def generate_valid_random_sighting_with_filter_data() -> SightingCreateBody:
    return SightingCreateBody(
        values=[generate_random_value() for _ in range(random.randint(1, 3))],
        source=None,
        timestamp=int(time.time()),
        filters=generate_random_search_query(),
    )
