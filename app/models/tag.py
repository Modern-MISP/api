from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import TINYINT

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    colour = Column(String)
    exportable = Column(TINYINT)
    org_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    hide_tag = Column(TINYINT)
    numerical_value = Column(Integer, index=True)
    is_galaxy = Column(TINYINT)
    is_custom_galaxy = Column(TINYINT)
    attribute_count = Column(Integer)  # new
    count = Column(Integer)  # new
    favourite = Column(TINYINT)  # new
    local_only = Column(TINYINT)  # new
