from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import TINYINT
from ..database import Base


class SharingGroupServer(Base):
    __tablename__ = "sharing_group_servers"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    server_id = Column(Integer)
    all_orgs = Column(TINYINT)
