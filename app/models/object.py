from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Object(Base):
    __tablename__ = "objects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"))

    feed = relationship("Feed")
