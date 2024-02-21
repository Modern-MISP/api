from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker

from mmisp.config import config

url = make_url(config.DATABASE_URL)

engine = create_engine(url, pool_size=100, max_overflow=20)

session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def get_db() -> Session:
    return session()
