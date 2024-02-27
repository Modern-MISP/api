from sqlalchemy import Column, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.util.uuid import uuid


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(255), unique=True, default=uuid)
    attribute_id = Column(Integer, ForeignKey("attributes.id"), index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), index=True, nullable=False)
    date_sighting = Column(Integer, nullable=False)
    source = Column(String(255), index=True, default="")
    type = Column(Integer, index=True, default=0)
