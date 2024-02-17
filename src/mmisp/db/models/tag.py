from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.util.uuid import uuid


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    colour = Column(String(255), nullable=False)
    exportable = Column(Boolean, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), default=0)
    user_id = Column(Integer, ForeignKey("users.id"), default=0)
    hide_tag = Column(Boolean, default=0)
    numerical_value = Column(Integer, index=True)
    inherited = Column(Integer)
    is_galaxy = Column(Boolean, default=False)
    is_custom_galaxy = Column(Boolean, default=False)
