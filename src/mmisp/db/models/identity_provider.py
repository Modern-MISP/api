from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database import Base


class OIDCIdentityProvider(Base):
    __tablename__ = "oidc_identity_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    org_id = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    base_url = Column(String(255), nullable=False)
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    scope = Column(String(255))
    """Possibility to add more scopes to be requested from the idp in addition to the default scopes,
    currently not used."""
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
