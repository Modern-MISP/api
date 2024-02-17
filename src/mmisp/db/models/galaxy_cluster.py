from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base
from .galaxy import Galaxy
from .organisation import Organisation
from .sharing_group import SharingGroup


class GalaxyCluster(Base):
    __tablename__ = "galaxy_clusters"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, index=True)
    collection_uuid = Column(String(255), nullable=True, index=True)
    type = Column(String(255), nullable=False, index=True)
    value = Column(String(255), nullable=False, index=True)
    tag_name = Column(String(255), nullable=False, default="", index=True)
    description = Column(String(255), nullable=False)
    galaxy_id = Column(Integer, ForeignKey(Galaxy.id, ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(255), nullable=False, default="")
    authors = Column(String(255), nullable=False)
    version = Column(Integer, default=0)
    distribution = Column(Integer)
    sharing_group_id = Column(Integer, ForeignKey(SharingGroup.id), nullable=True)
    org_id = Column(Integer, ForeignKey(Organisation.id), nullable=True)
    orgc_id = Column(Integer, ForeignKey(Organisation.id), nullable=True)
    default = Column(Boolean)
    locked = Column(Boolean)
    extends_uuid = Column(String(255))
    extends_version = Column(Integer)
    published = Column(Boolean)
    deleted = Column(Boolean)


class GalaxyElement(Base):
    __tablename__ = "galaxy elements"

    id = Column(Integer, primary_key=True)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, default="", index=True)
    value = Column(String(255), nullable=False, index=True)


class GalaxyReference(Base):
    __tablename__ = "galaxy references"

    id = Column(Integer, primary_key=True)
    galaxy_cluster_id = Column(Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True)
    referenced_galaxy_cluster_id = Column(Integer, nullable=False, index=True)
    referenced_galaxy_cluster_uuid = Column(String(255), nullable=False, index=True)
    referenced_galaxy_cluster_type = Column(String(255), nullable=False, index=True)
    referenced_galaxy_cluster_value = Column(String(255), nullable=False, index=True)
