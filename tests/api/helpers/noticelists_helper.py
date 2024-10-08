import json
import random
import string

from sqlalchemy import func, select

from mmisp.db.models.noticelist import Noticelist, NoticelistEntry


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


async def get_non_existing_noticelist_ids(db, number: int = 10) -> list:
    noticelist_ids = []
    largest_id = (await db.execute(select(func.max(Noticelist.id)))).scalar()
    print(largest_id)
    if not largest_id:
        largest_id = 1
    for i in range(1, number + 1):
        noticelist_ids.append(largest_id + i * random.randint(1, 9))
    return noticelist_ids


def get_invalid_noticelist_ids(number: int = 10) -> list:
    length = 5
    invalid_noticelist_ids = []
    for i in range(number):
        invalid_noticelist_ids.append("".join(random.choices(string.ascii_letters, k=length)))
    return invalid_noticelist_ids


def generate_random_noticelist_input() -> Noticelist:
    return Noticelist(
        name=random_string(),
        expanded_name=random_string(),
        ref=json.dumps([random_string()]),
        geographical_area=json.dumps([random_string()]),
        version=random.randint(1, 10),
        enabled=True,
    )


def generate_random_noticelistentry_input(noticelist_id: int) -> NoticelistEntry:
    scope = [random_string(), random_string(), random_string()]
    field = [random_string(), random_string(), random_string()]
    value = [random_string(), random_string(), random_string()]
    tags = [random_string(), random_string(), random_string()]
    message = json.dumps({"en": random_string()})

    return NoticelistEntry(
        noticelist_id=noticelist_id,
        data=json.dumps({"scope": scope, "field": field, "value": value, "tags": tags, "message": message}),
    )


async def add_noticelists(db, number: int = 10) -> list[int]:
    noticelist_ids = []
    for i in range(number):
        new_noticelist = generate_random_noticelist_input()
        db.add(new_noticelist)
        await db.flush()
        await db.refresh(new_noticelist)
        for j in range(random.randint(0, 10)):
            db.add(generate_random_noticelistentry_input(new_noticelist.id))
        await db.commit()
        noticelist_ids.append(new_noticelist.id)

    return noticelist_ids


async def remove_noticelists(db, ids: list[int]) -> None:
    for id in ids:
        noticelist = await db.get(Noticelist, id)
        await db.delete(noticelist)
        await db.commit()
