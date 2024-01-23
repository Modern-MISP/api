from sqlalchemy import Column, Integer, String

from ..database import Base


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255))
    name = Column(String(255))
    type = Column(String(255))
    description = Column(String(255))
    version = Column(String(255))
    icon = Column(String(255))
    namespace = Column(String(255))
    kill_chain_order = Column(String(255))  # must be serialized
