from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from mmisp.config import config

url = make_url(config.DATABASE_URL).set(drivername="mysql+mysqlconnector")
engine = create_engine(url)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables() -> None:
    try:
        with engine.connect():
            Base.metadata.create_all(bind=engine)
    except OperationalError:
        pass


def get_db() -> Iterator[Session]:
    db = session()
    try:
        yield db
    finally:
        db.close()
