from sqlalchemy import Boolean, Column, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    name = Column(String(255), unique=True)
    colour = Column(String(255))
    exportable = Column(Boolean)
    org_id = Column(Integer, index=True, default=0)
    user_id = Column(Integer, index=True, default=0)
    hide_tag = Column(Boolean, default=0)
    numerical_value = Column(Integer, index=True)
    inherited = Column(Integer, nullable=True)
    is_galaxy = Column(Boolean, default=False)
    is_custom_galaxy = Column(Boolean, default=False)
    # attribute_count = Column(Integer)  # new
    # count = Column(Integer)  # new
    # favourite = Column(Boolean)  # new
    # local_only = Column(Boolean)  # new
