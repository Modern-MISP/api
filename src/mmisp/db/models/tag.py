from sqlalchemy import Column, Integer, String

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    colour = Column(String(255))
    exportable = Column(Integer)
    org_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    hide_tag = Column(Integer)
    numerical_value = Column(Integer, index=True)
    is_galaxy = Column(Integer)
    is_custom_galaxy = Column(Integer)
    attribute_count = Column(Integer)  # new
    count = Column(Integer)  # new
    favourite = Column(Integer)  # new
    local_only = Column(Integer)  # new
