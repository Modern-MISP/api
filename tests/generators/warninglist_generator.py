import random
import string

from src.mmisp.api_schemas.warninglists.create_warninglist_body import CreateWarninglistBody
from src.mmisp.api_schemas.warninglists.warninglist_response import Category, Type
from src.mmisp.db.models.warninglist import Warninglist, WarninglistEntry

from mmisp.api_schemas.warninglists.toggle_enable_warninglists_body import ToggleEnableWarninglistsBody
from mmisp.db.database import get_db
from mmisp.util.partial import partial


def generate_number_string() -> str:
    number = random.randint(1, 21)
    return str(number)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_value(length: int = 15) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits))


def random_type() -> str:
    return random.choice(list(Type)).value


def random_Category() -> str:
    return random.choice(list(Category)).value


def generate_random_valid_warninglist_data() -> CreateWarninglistBody:
    return CreateWarninglistBody(
        name=random_string(),
        type=random_type(),
        description=random_string(50),
        default=bool(random.getrandbits),
        category=random_Category(),
        valid_attributes=random_string(5),
        values=random_string(),
    )


def generate_random_invalid_warninglist_data() -> dict:
    input_list = [
        random_string(),
        random_type(),
        random_string(50),
        random_Category(),
        bool(random.getrandbits),
        random_string(5),
        random_string(),
    ]

    random_list = [0, 1, 2, 3, 4, 5, 6]
    for number in random.sample(random_list, random.randint(1, len(input_list))):
        input_list[number] = None

    return partial(CreateWarninglistBody)(
        name=input_list[0],
        type=input_list[1],
        description=input_list[2],
        category=input_list[3],
        default=input_list[4],
        accepted_attribute_type=input_list[5],
        values=input_list[6],
    )


def generate_random_warninglist_input() -> Warninglist:
    return Warninglist(
        name=random_string(),
        type=random_type(),
        description=random_string(50),
        version=1,
        enabled=bool(random.getrandbits),
        default=bool(random.getrandbits),
        category=random_Category(),
        warninglist_entry_count=random.randint(1, 10),
        valid_attributes=random_string(),
    )


def generate_random_warninglistentry_input(warninglist_id: int) -> WarninglistEntry:
    return WarninglistEntry(
        value=random_string(),
        warninglist_id=str(warninglist_id),
        comment=random_string(),
    )


def add_warninglists(number: int = 1) -> list[int]:
    db = get_db()
    warninglist_ids = []
    for i in range(number):
        new_warninglist = generate_random_warninglist_input()
        db.add(new_warninglist)
        db.flush()
        db.refresh(new_warninglist)
        for j in range(new_warninglist.warninglist_entry_count):
            db.add(generate_random_warninglistentry_input(new_warninglist.id))
        db.commit()
        warninglist_ids.append(new_warninglist.id)

    return warninglist_ids


# def remove_warninglists(ids: list[int]) -> None:
#     db = get_db()
#     for id in ids:
#         db.get(Warninglist).


def generate_togglelist() -> ToggleEnableWarninglistsBody:
    return ToggleEnableWarninglistsBody(
        id=["249", "250", "251"],
        name="cqzZI32ZKy",
        enabled=0,
    )
