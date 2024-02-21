from functools import wraps
from typing import Any, Callable

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from mmisp.config import config

url = make_url(config.DATABASE_URL)
engine = create_engine(url, pool_size=100, max_overflow=20)

session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    return session()


def with_session_management(fn: Callable) -> Callable:
    @wraps(fn)
    async def wrapper(*args, **kwargs) -> Any:
        db: Session = kwargs.pop("db")
        output: Any = None

        with db:
            output = await fn(*args, **kwargs, db=db)

        return output

    return wrapper
