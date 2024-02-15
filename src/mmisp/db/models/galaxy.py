from sqlalchemy import Boolean, Column, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255), nullable=False, default="", index=True)
    type = Column(String(255), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=False, default="")
    namespace = Column(String(255), nullable=False, default="misp", index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    kill_chain_order = Column(String(255))  # must be serialized
