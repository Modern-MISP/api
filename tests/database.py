from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from mmisp.config import config
from mmisp.db.database import Base, engine
from mmisp.db.models import (  # noqa: F401
    attribute,
    auth_key,
    event,
    feed,
    galaxy,
    identity_provider,
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

# url = make_url(config.DATABASE_URL).set(drivername="mysql+mysqlconnector")
url = make_url(config.DATABASE_URL)
# engine = create_engine(url, pool_size=100, max_overflow=20)
engine = create_engine(url)  # noqa: F811
sm = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base.metadata.create_all(engine)


#    session.rollback()
#    session.close()
