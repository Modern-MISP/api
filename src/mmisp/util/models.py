from enum import Enum
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def update_record(record: T, update: dict) -> None:
    for key, value in update.items():
        if value is None:
            continue

        setattr(record, key, value if not isinstance(value, Enum) else value.value)
