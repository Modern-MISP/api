from sqlalchemy import Column, String

from ..database import Base


class Sighting(Base):
    __tablename__ = "sightings"
    id = Column(String, primary_key=True)
    attribute_id = Column(String)
    event_id = Column(String)
    org_id = Column(String)
    date_sighting = Column(String)
    uuid = Column(String)
    source = Column(String)
    type = Column(String)
    attribute_uuid = Column(String)

    class Organisation:
        id = Column(String, primary_key=True)
        uuid = Column(String)
        name = Column(String)
