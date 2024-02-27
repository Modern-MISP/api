from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.util.uuid import uuid


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    colour = Column(String(255), nullable=False)
    exportable = Column(Boolean, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hide_tag = Column(Boolean, default=False, nullable=False)
    numerical_value = Column(Integer, index=True)

    local_only = Column(Integer)
    is_galaxy = Column(Boolean, default=False)
    is_custom_galaxy = Column(Boolean, default=False)
