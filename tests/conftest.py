from typing import Generator

import pytest
from sqlalchemy.orm import Session

from tests.database import get_db


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    with get_db() as db:
        yield db
