from uuid import uuid4 as _uuid4


def uuid() -> str:
    return _uuid4().__str__()
