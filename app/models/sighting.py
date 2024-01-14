from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from ..database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True)
    attribute_id = Column(String)
    event_id = Column(String)
    org_id = Column(String, ForeignKey("organisations.id"))
    date_sighting = Column(String)
    uuid = Column(String)
    source = Column(String)
    type = Column(String)
    attribute_uuid = Column(String)

    organisation = relationship("Organisation")


class SightingCoreConfig(Base):
    __tablename__ = "sighting_core_configs"

    id = Column(Integer, primary_key=True)
    sighting_id = Column(String, ForeignKey("sightings.id"))
    estimative_language_confidence_in_analytic_judgment = Column(Float)
    estimative_language_likelihood_probability = Column(Float)
    phishing_psychological_acceptability = Column(Float)
    phishing_state = Column(Float)


class SightingModelOverrides(Base):
    __tablename__ = "sighting_model_overrides"

    id = Column(Integer, primary_key=True)
    sighting_id = Column(String, ForeignKey("sightings.id"))
    lifetime = Column(Integer)
    decay_speed = Column(Float)
    threshold = Column(Integer)
    default_base_score = Column(Integer)

    core_config = relationship("SightingCoreConfig", uselist=False)
