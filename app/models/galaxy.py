from sqlalchemy import Column, Integer, String

from ..database import Base


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    name = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(String)
    icon = Column(String)
    namespace = Column(String)
    kill_chain_order = Column(String)  # must be serialized
