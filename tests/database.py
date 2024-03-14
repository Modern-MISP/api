from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from mmisp.config import config

url = make_url(config.DATABASE_URL)

if "mysql" in url.drivername:
    url = url.set(drivername="mysql+mysqlconnector")
if "sqlite" in url.drivername:
    url = url.set(drivername="sqlite")

engine = create_engine(url, poolclass=NullPool)
session = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def get_db() -> Session:
    return session()
