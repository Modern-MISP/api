from sqlalchemy import Boolean, Column, String, Integer

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(String, primary_key=True)
    name = Column(String)
    colour = Column(String)
    exportable = Column(Boolean)
    org_id = Column(String)
    user_id = Column(String)
    hide_tag = Column(Boolean)
    numerical_value = Column(String)
    is_galaxy = Column(Boolean)
    is_custom_galaxy = Column(Boolean)
    inherited = Column(Integer)
