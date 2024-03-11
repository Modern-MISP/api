from time import time

from nanoid import generate

from mmisp.db.models.server import Server
from mmisp.util.uuid import uuid


def generate_server() -> Server:
    """These fields need to be set manually: org_id"""
    return Server(
        name=f"test server {time()}-{uuid()}",
        url=f"http://{time()}-{uuid()}.server.mmisp.service",
        authkey=generate(),
        push=False,
        pull=False,
        push_sightings=False,
        # push_galaxy_clusters = Column(Boolean)
        # pull_galaxy_clusters = Column(Boolean)
        # organization = Column(String(255))
        remote_org_id=0,
        self_signed=False,
        pull_rules="",
        push_rules="",
        # cert_file = Column(String(255))
        # client_cert_file = Column(String(255))
    )
