from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from mmisp.config import config

url = make_url(config.DATABASE_URL)

create_engine_kwargs = {}

if url.drivername != "sqlite":
    create_engine_kwargs = {"pool_size": 100, "max_overflow": 20}

engine = create_engine(url, **create_engine_kwargs)

session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def get_db() -> Session:
    return session()
