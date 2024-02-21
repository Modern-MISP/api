from typing import Generator

import pytest
from sqlalchemy.orm import Session

from tests.database import sm


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    #    session = sm()
    yield sm()
