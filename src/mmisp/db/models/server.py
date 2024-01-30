from sqlalchemy import VARBINARY, Boolean, Column, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255))
    url = Column(String(255))
    authkey = Column(VARBINARY(255))
    org_id = Column(Integer)
    push = Column(Boolean)
    pull = Column(Boolean)
    push_sightings = Column(Boolean)
    push_galaxy_clusters = Column(Boolean)
    pull_galaxy_clusters = Column(Boolean)
    lastpulledid = Column(Integer)
    lastpushedid = Column(Integer)
    organization = Column(String(255))
    remote_org_id = Column(Integer)
    publish_without_email = Column(Boolean)
    unpublish_event = Column(Boolean)
    self_signed = Column(Boolean)
    pull_rules = Column(String(255))
    push_rules = Column(String(255))
    cert_file = Column(String(255))
    client_cert_file = Column(String(255))
    internal = Column(Boolean)
    skip_proxy = Column(Boolean)
    remove_missing_tags = Column(Boolean)
    caching_enabled = Column(Boolean)
    priority = Column(Integer)
