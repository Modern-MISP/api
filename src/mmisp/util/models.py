from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def update_record(record: T, update: dict) -> None:
    for key, value in update.items():
        new_value = getattr(record, key)

        if value is not None:
            new_value = value

        setattr(record, key, new_value)
