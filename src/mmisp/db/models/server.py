from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import TINYINT, VARBINARY
from ..database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    name = Column(String)
    url = Column(String)
    authkey = Column(VARBINARY)
    org_id = Column(Integer)
    push = Column(TINYINT)
    pull = Column(TINYINT)
    push_sightings = Column(TINYINT)
    push_galaxy_clusters = Column(TINYINT)
    pull_galaxy_clusters = Column(TINYINT)
    lastpulledid = Column(Integer)
    lastpushedid = Column(Integer)
    organization = Column(String)
    remote_org_id = Column(Integer)
    publish_without_email = Column(TINYINT)
    unpublish_event = Column(TINYINT)
    self_signed = Column(TINYINT)
    pull_rules = Column(String)
    push_rules = Column(String)
    cert_file = Column(String)
    client_cert_file = Column(String)
    internal = Column(TINYINT)
    skip_proxy = Column(TINYINT)
    remove_missing_tags = Column(TINYINT)
    caching_enabled = Column(TINYINT)
    priority = Column(Integer)
