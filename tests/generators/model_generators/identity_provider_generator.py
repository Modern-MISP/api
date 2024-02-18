from time import time_ns

from mmisp.db.models.identity_provider import OIDCIdentityProvider
from mmisp.util.uuid import uuid


def generate_oidc_identity_provider() -> OIDCIdentityProvider:
    """These fields need to be set manually: org_id"""
    return OIDCIdentityProvider(
        name="Test Identity Provider",
        active=True,
        base_url=f"https://{time_ns()}.test-idp.kit.service",
        client_id=uuid(),
        client_secret=uuid(),
        scope="",
    )
