import json
import random
import string

from sqlalchemy import func
from sqlalchemy.orm import Session
from src.mmisp.db.models.noticelist import Noticelist, NoticelistEntry

from mmisp.db.database import get_db


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def get_non_existing_noticelist_ids(number: int = 10) -> list:
    db: Session = get_db()
    noticelist_ids = []
    largest_id = db.query(func.max(Noticelist.id)).scalar()
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
        ref=json.dumps(random_string()),
        geographical_area=json.dumps(random_string()),
        version=random.randint(1, 10),
        # At creation always on true for TestToggleEnableNoticelist
        enabled=True,
    )


def generate_random_noticelistentry_input(noticelist_id: int) -> NoticelistEntry:
    return NoticelistEntry(
        noticelist_id=str(noticelist_id),
        scope=json.dumps([random_string(), random_string(), random_string()]),
        field=json.dumps([random_string(), random_string(), random_string()]),
        value=json.dumps([random_string(), random_string(), random_string()]),
        tags=json.dumps([random_string(), random_string(), random_string()]),
        message=random_string(),
    )


def add_noticelists(number: int = 10) -> list[int]:
    db = get_db()
    noticelist_ids = []
    for i in range(number):
        new_noticelist = generate_random_noticelist_input()
        db.add(new_noticelist)
        db.flush()
        db.refresh(new_noticelist)
        for j in range(random.randint(0, 10)):
            db.add(generate_random_noticelistentry_input(new_noticelist.id))
        db.commit()
        noticelist_ids.append(new_noticelist.id)

    return noticelist_ids


def remove_noticelists(ids: list[int]) -> None:
    db = get_db()
    for id in ids:
        noticelist = db.get(Noticelist, id)
        db.delete(noticelist)
        db.commit()
