from sqlalchemy import VARBINARY, Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True)
    name = Column(String(255))
    url = Column(String(255))
    authkey = Column(VARBINARY(255))
    org_id = Column(Integer)
    push = Column(TINYINT)
    pull = Column(TINYINT)
    push_sightings = Column(TINYINT)
    push_galaxy_clusters = Column(TINYINT)
    pull_galaxy_clusters = Column(TINYINT)
    lastpulledid = Column(Integer)
    lastpushedid = Column(Integer)
    organization = Column(String(255))
    remote_org_id = Column(Integer)
    publish_without_email = Column(TINYINT)
    unpublish_event = Column(TINYINT)
    self_signed = Column(TINYINT)
    pull_rules = Column(String(255))
    push_rules = Column(String(255))
    cert_file = Column(String(255))
    client_cert_file = Column(String(255))
    internal = Column(TINYINT)
    skip_proxy = Column(TINYINT)
    remove_missing_tags = Column(TINYINT)
    caching_enabled = Column(TINYINT)
    priority = Column(Integer)
