from sqlalchemy import Column, String

from ..database import Base


class OrganisationSchema(Base):
    __tablename__ = "sighting_organisation"
    id = Column(String)
    uuid = Column(String)
    name = Column(String)


class SightingSchema(Base):
    __tablename__ = "sightings"
    id = Column(String)
    attribute_id = Column(String)
    event_id = Column(String)
    org_id = Column(String)
    date_sighting = Column(String)
    uuid = Column(String)
    source = Column(String)
    type = Column(String)
    attribute_uuid = Column(String)
    Organisation: OrganisationSchema

    class Config:
        orm_mode = True


class SightingDeleteSchema(Base):
    __tablename__ = "delete_sightings"
    saved = Column(String)
    success = Column(String)
    name = Column(String)
    message = Column(String)
    url = Column(String)
