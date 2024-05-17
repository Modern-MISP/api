import random
import string
from typing import Any

from sqlalchemy import func

from mmisp.api_schemas.tags.create_tag_body import TagCreateBody
from mmisp.db.models.tag import Tag


def generate_number() -> int:
    number = random.randint(1, 4)
    return number


def random_string_with_punctuation(length: int = 10) -> str:
    return random_string(length - 1) + "++"


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_hexcolour(length: int = 6) -> str:
    return "#" + "".join(random.choices(string.hexdigits, k=length))


def generate_valid_required_tag_data(*args) -> TagCreateBody:
    return TagCreateBody(
        name=random_string(),
        colour=random_hexcolour(),
        exportable=bool(random.getrandbits),
    )


def generate_valid_tag_data(organisation, user) -> TagCreateBody:
    return TagCreateBody(
        name=random_string(),
        colour=random_hexcolour(),
        exportable=bool(random.getrandbits),
        org_id=organisation.id,
        user_id=user.id,
        hide_tag=bool(random.getrandbits),
        numerical_value=generate_number(),
        inherited=bool(random.getrandbits),
    )


def generate_invalid_tag_data() -> Any:
    input_list = [
        random_string(),
        random_hexcolour(6),
        bool(random.getrandbits),
    ]
    random_list = [0, 1, 2]
    for number in random.sample(random_list, random.randint(1, len(input_list) - 1)):
        input_list[number] = None

    return {"name": input_list[0], "colour": input_list[1], "exportable": input_list[2]}


def get_non_existing_tags(db, number: int = 5) -> list:
    tag_ids: list[int] = []
    largest_id = db.query(func.max(Tag.id)).scalar()
    print(largest_id)
    if not largest_id:
        largest_id = 1
    for i in range(1, number + 1):
        tag_ids.append(largest_id + i * random.randint(1, 9))
    print(tag_ids)
    return tag_ids


def get_invalid_tags(number: int = 5) -> list:
    length = 5
    invalid_tags: list[str] = []
    for i in range(number):
        invalid_tags.append("".join(random.choices(string.ascii_letters, k=length)))
    return invalid_tags


def remove_tags(db, ids: list[int]) -> None:
    for id in ids:
        tag = db.get(Tag, id)
        if tag is not None:
            db.delete(tag)

    db.commit()
