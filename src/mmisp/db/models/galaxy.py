from sqlalchemy import Boolean, Column, Integer, String, Text

from mmisp.util.uuid import uuid

from ..database import Base


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), nullable=False, unique=True, default=uuid)
    name = Column(String(255), nullable=False, default="", index=True)
    type = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    version = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=False, default="")
    namespace = Column(String(255), nullable=False, default="misp", index=True)
    kill_chain_order = Column(String(255))
    """must be serialized"""
    enabled = Column(Boolean, nullable=False, default=True)
    local_only = Column(Boolean, default=False)
