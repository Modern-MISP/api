from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import TINYINT
from ..database import Base


class Feed(Base):
    __tablename__ = "sharing_group_orgs"

    id = Column(Integer, primary_key=True)
    sharing_group_id = Column(Integer)
    org_id = Column(Integer)
    extend = Column(TINYINT)
