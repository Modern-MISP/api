from functools import wraps
from typing import Any, Callable, TypeAlias

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from mmisp.config import config

Session: TypeAlias = AsyncSession

url = make_url(config.DATABASE_URL)
engine = create_async_engine(url, poolclass=NullPool)
async_session = sessionmaker(autoflush=False, expire_on_commit=False, class_=AsyncSession, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    return async_session()


def with_session_management(fn: Callable) -> Callable:
    @wraps(fn)
    async def wrapper(*args, **kwargs) -> Any:
        db: Session = kwargs.pop("db")
        output: Any = None

        try:
            output = await fn(*args, **kwargs, db=db)
        finally:
            await db.close()

        return output

    return wrapper


async def create_all_models() -> None:
    async with engine.begin() as db:
        await db.run_sync(Base.metadata.create_all)
