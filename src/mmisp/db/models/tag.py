from sqlalchemy import Boolean, Column, Integer, String

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    colour = Column(String(255))
    exportable = Column(Boolean)
    org_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    hide_tag = Column(Boolean)
    numerical_value = Column(Integer, index=True)
    is_galaxy = Column(Boolean)
    is_custom_galaxy = Column(Boolean)
    attribute_count = Column(Integer)  # new
    count = Column(Integer)  # new
    favourite = Column(Boolean)  # new
    local_only = Column(Boolean)  # new
