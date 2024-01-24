from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .organisation import Organisation
from ..database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, index=True)
    event_id = Column(Integer, index=True)
    org_id = Column(Integer, ForeignKey(Organisation.id), index=True)
    date_sighting = Column(BigInteger)
    uuid = Column(String(255), unique=True)
    source = Column(String(255), index=True)
    type = Column(Integer, index=True)
    attribute_uuid = Column(String(255))

    organisation = relationship("Organisation")


class SightingCoreConfig(Base):
    __tablename__ = "sighting_core_configs"

    id = Column(Integer, primary_key=True)
    sighting_id = Column(Integer, ForeignKey(Sighting.id), index=True)
    estimative_language_confidence_in_analytic_judgment = Column(Float)
    estimative_language_likelihood_probability = Column(Float)
    phishing_psychological_acceptability = Column(Float)
    phishing_state = Column(Float)


class SightingModelOverrides(Base):
    __tablename__ = "sighting_model_overrides"

    id = Column(Integer, primary_key=True)
    sighting_id = Column(Integer, ForeignKey(Sighting.id), index=True)
    lifetime = Column(Integer)
    decay_speed = Column(Float)
    threshold = Column(Float)
    default_base_score = Column(Integer)

    core_config = relationship("SightingCoreConfig", uselist=False)
