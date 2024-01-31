from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from mmisp.config import config

url = make_url(config.DATABASE_URL).set(drivername="mysql+mysqlconnector")
engine = create_engine(url)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    return session()
