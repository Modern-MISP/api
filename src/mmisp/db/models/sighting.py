from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.util.uuid import uuid

from .attribute import Attribute
from .event import Event
from .organisation import Organisation


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True, nullable=False)
    uuid = Column(String(40), unique=True, default=uuid)
    attribute_id = Column(Integer, ForeignKey(Attribute.id), index=True, nullable=False)
    event_id = Column(Integer, ForeignKey(Event.id), index=True, nullable=False)
    org_id = Column(Integer, ForeignKey(Organisation.id), index=True, nullable=False)
    date_sighting = Column(BigInteger, nullable=False)
    source = Column(String(255), index=True, default="")
    type = Column(Integer, index=True, default=0)
