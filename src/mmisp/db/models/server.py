from sqlalchemy import VARBINARY, Boolean, Column, Integer, String

# from mmisp.util.uuid import uuid
from ..database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    authkey = Column(VARBINARY(255), nullable=False)
    org_id = Column(Integer, nullable=False)
    push = Column(Boolean, nullable=False)
    pull = Column(Boolean, nullable=False)
    push_sightings = Column(Boolean, nullable=False)
    push_galaxy_clusters = Column(Boolean)
    pull_galaxy_clusters = Column(Boolean)
    lastpulledid = Column(Integer)
    lastpushedid = Column(Integer)
    organization = Column(String(255))
    remote_org_id = Column(Integer, nullable=False)
    publish_without_email = Column(Boolean, nullable=False, default=False)
    unpublish_event = Column(Boolean, nullable=False, default=False)
    self_signed = Column(Boolean, nullable=False)
    pull_rules = Column(String(255), nullable=False)
    push_rules = Column(String(255), nullable=False)
    cert_file = Column(String(255))
    client_cert_file = Column(String(255))
    internal = Column(Boolean, nullable=False, default=False)
    skip_proxy = Column(Boolean, nullable=False, default=False)
    caching_enabled = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0)
