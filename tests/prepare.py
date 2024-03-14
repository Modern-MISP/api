from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError

from mmisp.config import config

url = make_url(config.DATABASE_URL).set(database="", drivername="mysql+mysqlconnector")
database = make_url(config.DATABASE_URL).database
engine = create_engine(url)

with engine.connect() as conn:
    try:
        conn.execute(text(f"DROP DATABASE IF EXISTS `{database}`"))
    except ProgrammingError as e:
        print(f"Skipping drop database due to: {e}")

    try:
        conn.execute(text(f"CREATE DATABASE `{database}`"))
    except ProgrammingError as e:
        print(f"Skipping create database due to: {e}")
