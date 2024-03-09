from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from mmisp.db.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    colour = Column(String(255), nullable=False)
    exportable = Column(Boolean, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=None)
    hide_tag = Column(Boolean, default=False, nullable=False)
    numerical_value = Column(Integer, index=True)
    is_galaxy = Column(Boolean, default=False)
    is_custom_galaxy = Column(Boolean, default=False)
    local_only = Column(Boolean, default=False)
