import re
from uuid import uuid4 as _uuid4


def uuid() -> str:
    return str(_uuid4())


def is_uuid(_uuid: str) -> bool:
    return bool(re.search("^([a-zA-Z0-9]){8}(-([a-zA-Z0-9]){4}){3}-([a-zA-Z0-9]){12}$", _uuid))
