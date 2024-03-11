from sqlalchemy import Boolean, Column, Integer, String

from mmisp.db.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    colour = Column(String(7), nullable=False)
    exportable = Column(Boolean, nullable=False)
    org_id = Column(Integer, nullable=False, default=0, index=True)
    user_id = Column(Integer, nullable=False, default=0, index=True)
    hide_tag = Column(Boolean, nullable=False, default=False)
    numerical_value = Column(Integer, index=True)
    is_galaxy = Column(Boolean, default=False)
    is_custom_galaxy = Column(Boolean, default=False)
    local_only = Column(Boolean, default=False)
