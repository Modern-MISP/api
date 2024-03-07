import random
import string

from sqlalchemy import func
from sqlalchemy.orm import Session
from tests.database import get_db
from tests.generators.model_generators.warninglist_generator import (
    generate_warninglist,
    generate_warninglist_entry,
    generate_warninglist_type,
)

from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.db.models.warninglist import Warninglist


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def add_warninglists(number: int = 10) -> list[int]:
    db = get_db()

    warninglist_ids = []

    for i in range(number):
        new_warninglist = generate_warninglist()
        new_warninglist.warninglist_entry_count = random.randint(1, 10)

        db.add(new_warninglist)
        db.flush()
        db.refresh(new_warninglist)

        for j in range(random.randint(1, 10)):
            entry = generate_warninglist_entry()
            entry.warninglist_id = new_warninglist.id
            db.add(entry)

        for j in range(random.randint(1, 10)):
            type = generate_warninglist_type()
            type.warninglist_id = new_warninglist.id
            db.add(type)

        db.commit()

        warninglist_ids.append(new_warninglist.id)

    return warninglist_ids


def remove_warninglists(ids: list[int]) -> None:
    db = get_db()

    db.query(Warninglist).filter(Warninglist.id.in_(ids)).delete(False)

    db.commit()


def generate_enable_warning_lists_body(ids: list[int]) -> ToggleEnableWarninglistsBody:
    partial_ids = random.choices(ids)
    warninglist_ids = [str(id) for id in partial_ids]

    return ToggleEnableWarninglistsBody(
        id=warninglist_ids,
        name="cqzZI32ZKy",
        enabled=bool(random.getrandbits),
    )


def get_largest_id() -> int:
    db: Session = get_db()
    largest_id = db.query(func.max(Warninglist.id)).scalar()
    if not largest_id:
        largest_id = 1

    return largest_id
