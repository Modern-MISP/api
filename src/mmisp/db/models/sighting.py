from sqlalchemy import Column, ForeignKey, Integer, String

from mmisp.util.uuid import uuid

from ..database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), unique=True, default=uuid)
    attribute_id = Column(Integer, ForeignKey("attributes.id"), index=True, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id"), index=True, nullable=False)
    date_sighting = Column(Integer, nullable=False)
    source = Column(String(255), index=True)
    type = Column(Integer, index=True, default=0)


# class SightingCoreConfig(Base):
#     __tablename__ = "sighting_core_configs"

#     id = Column(Integer, primary_key=True)
#     sighting_id = Column(Integer, ForeignKey(Sighting.id), index=True)
#     estimative_language_confidence_in_analytic_judgment = Column(Float)
#     estimative_language_likelihood_probability = Column(Float)
#     phishing_psychological_acceptability = Column(Float)
#     phishing_state = Column(Float)


# class SightingModelOverrides(Base):
#     __tablename__ = "sighting_model_overrides"

#     id = Column(Integer, primary_key=True)
#     sighting_id = Column(Integer, ForeignKey(Sighting.id), index=True)
#     lifetime = Column(Integer)
#     decay_speed = Column(Float)
#     threshold = Column(Float)
#     default_base_score = Column(Integer)

#     # core_config = relationship("SightingCoreConfig", uselist=False)
