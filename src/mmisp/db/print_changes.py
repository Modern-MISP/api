#!/usr/bin/env python3

"""
USAGE:
    - Create env file with the variables
        MYSQL_USER
        MYSQL_PASSWORD
        MYSQL_HOST
        MYSQL_DBNAME
    - Populate your environment `export $(cat ENVFILE)`
    - Run `python -m mmisp.db.print_changes`
"""


import os
import pprint

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import MetaData, create_engine

from .database import Base

# import all models, so Base is populated
from .models import (  # noqa: F401
    attribute,
    auth_key,
    event,
    feed,
    galaxy,
    galaxy_cluster,
    noticelist,
    object,
    organisation,
    role,
    server,
    sharing_group,
    sighting,
    tag,
    taxonomy,
    user,
    user_setting,
    warninglist,
)

myuser = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
db_name = os.getenv("MYSQL_DBNAME")

engine = create_engine(f"mysql+mysqlconnector://{myuser}:{password}@{host}/{db_name}")


metadata = MetaData()

mc = MigrationContext.configure(engine.connect())

diff = compare_metadata(mc, Base.metadata)
pprint.pprint(diff, indent=2, width=20)
