from uuid import uuid4 as _uuid4


def uuid() -> str:
    return str(_uuid4())
