from sqlalchemy import VARCHAR, Boolean, Column, Integer, Text

from ..database import Base


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    url = Column(VARCHAR(255), nullable=False)
    authkey = Column(VARCHAR(40), nullable=False)
    org_id = Column(Integer, nullable=False, index=True)
    push = Column(Boolean, nullable=False)
    pull = Column(Boolean, nullable=False)
    push_sightings = Column(Boolean, nullable=False, default=False)
    push_galaxy_clusters = Column(Boolean, default=False)
    pull_galaxy_clusters = Column(Boolean, default=False)
    lastpulledid = Column(Integer)
    lastpushedid = Column(Integer)
    organization = Column(VARCHAR(10), default=None)
    remote_org_id = Column(Integer, nullable=False, index=True)
    publish_without_email = Column(Boolean, nullable=False, default=False)
    unpublish_event = Column(Boolean, nullable=False, default=False)
    self_signed = Column(Boolean, nullable=False)
    pull_rules = Column(Text, nullable=False)
    push_rules = Column(Text, nullable=False)
    cert_file = Column(VARCHAR(255))
    client_cert_file = Column(VARCHAR(255))
    internal = Column(Boolean, nullable=False, default=False)
    skip_proxy = Column(Boolean, nullable=False, default=False)
    caching_enabled = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, nullable=False, default=0, index=True)
