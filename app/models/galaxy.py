from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from ..database import Base


class Galaxy(Base):
    __tablename__ = "galaxies"

    id = Column(String, primary_key=True)
    uuid = Column(String)
    name = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(String)
    icon = Column(String)
    namespace = Column(String)
    kill_chain_order = relationship("KillChainOrder")


class KillChainOrder(Base):
    __tablename__ = "kill_chain_order"

    order = Column(String)
