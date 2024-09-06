import random
import string

from sqlalchemy import delete, func, select

from mmisp.api_schemas.warninglists import ToggleEnableWarninglistsBody
from mmisp.db.models.warninglist import Warninglist
from mmisp.tests.generators.model_generators.warninglist_generator import (
    generate_warninglist,
    generate_warninglist_entry,
    generate_warninglist_type,
)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


async def add_warninglists(db, number: int = 5) -> list[int]:
    warninglist_ids = []

    for i in range(number):
        new_warninglist = generate_warninglist()
        new_warninglist.warninglist_entry_count = random.randint(1, 10)

        db.add(new_warninglist)
        await db.flush()
        await db.refresh(new_warninglist)

        for j in range(random.randint(1, 10)):
            entry = generate_warninglist_entry()
            entry.warninglist_id = new_warninglist.id
            db.add(entry)

        for j in range(random.randint(1, 10)):
            type = generate_warninglist_type()
            type.warninglist_id = new_warninglist.id
            db.add(type)

        await db.commit()

        warninglist_ids.append(new_warninglist.id)

    return warninglist_ids


async def remove_warninglists(db, ids: list[int]) -> None:
    await db.execute(delete(Warninglist).filter(Warninglist.id.in_(ids)))

    await db.commit()


def generate_enable_warning_lists_body(ids: list[int]) -> ToggleEnableWarninglistsBody:
    partial_ids = random.choices(ids)
    warninglist_ids = [str(id) for id in partial_ids]

    return ToggleEnableWarninglistsBody(
        id=warninglist_ids,
        name="cqzZI32ZKy",
        enabled=bool(random.getrandbits),
    )


async def get_largest_id(db) -> int:
    largest_id = (await db.execute(select(func.max(Warninglist.id)))).scalar()
    if not largest_id:
        largest_id = 1

    return largest_id
