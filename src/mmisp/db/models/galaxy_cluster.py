from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from mmisp.util.uuid import uuid

from ..database import Base
from .galaxy import Galaxy


class GalaxyCluster(Base):
    __tablename__ = "galaxy_clusters"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    collection_uuid = Column(String(255), nullable=False, index=True, default="0")
    type = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    tag_name = Column(String(255), nullable=False, default="", index=True)
    description = Column(Text, nullable=False)
    galaxy_id = Column(Integer, ForeignKey(Galaxy.id, ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(255), nullable=False, default="")
    authors = Column(Text, nullable=False)
    version = Column(Integer, default=0, index=True)
    distribution = Column(Integer, nullable=False, default=0)
    sharing_group_id = Column(Integer, index=True, default=0)
    org_id = Column(Integer, nullable=False, index=True, default=0)
    orgc_id = Column(Integer, nullable=False, index=True, default=0)
    default = Column(Boolean, nullable=False, default=False, index=True)
    locked = Column(Boolean, nullable=False, default=False)
    extends_uuid = Column(String(40), index=True)
    extends_version = Column(Integer, default=0, index=True)
    published = Column(Boolean, nullable=False, default=False)
    deleted = Column(Boolean, nullable=False, default=False)


class GalaxyElement(Base):
    __tablename__ = "galaxy_elements"

    id = Column(Integer, primary_key=True, nullable=False)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, default="", index=True)
    value = Column(Text, nullable=False)


class GalaxyReference(Base):
    __tablename__ = "galaxy_reference"

    id = Column(Integer, primary_key=True, nullable=False)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True)
    referenced_galaxy_cluster_id = Column(Integer, nullable=False, index=True)
    referenced_galaxy_cluster_uuid = Column(String(255), nullable=False, index=True)
    referenced_galaxy_cluster_type = Column(Text, nullable=False)
    referenced_galaxy_cluster_value = Column(Text, nullable=False)
