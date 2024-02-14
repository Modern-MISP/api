from sqlalchemy import Column, ForeignKey, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base
from .galaxy import Galaxy


class GalaxyCluster(Base):
    __tablename__ = "galaxy_clusters"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    collection_uuid = Column(String(255), nullable=False, index=True)
    type = Column(String(255), nullable=False, index=True)
    value = Column(String(255), nullable=False, index=True)
    tag_name = Column(String(255), nullable=False, default="", index=True)
    description = Column(String(255), nullable=False)
    galaxy_id = Column(Integer, ForeignKey(Galaxy.id), nullable=False, index=True)
    source = Column(String(255), nullable=False, default="")
    authors = Column(String(255), nullable=False)
    version = Column(Integer, default=0)


class GalaxyElement(Base):
    __tablename__ = "galaxy elements"

    id = Column(Integer, primary_key=True)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id), nullable=False, index=True)
    key = Column(String(255), nullable=False, default="", index=True)
    value = Column(String(255), nullable=False, index=True)


class GalaxyReference(Base):
    __tablename__ = "galaxy references"

    id = Column(Integer, primary_key=True)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id), nullable=False, index=True)
    referenced_galaxy_cluster_id = Column(Integer, nullable=False, index=True)
    referenced_galaxy_cluster_uuid = Column(String(255), nullable=False, index=True)
    referenced_galaxy_cluster_type = Column(String(255), nullable=False, index=True)
    referenced_galaxy_cluster_value = Column(String(255), nullable=False, index=True)
