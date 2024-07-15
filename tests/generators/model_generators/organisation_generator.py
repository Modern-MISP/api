from time import time

from mmisp.db.models.organisation import Organisation
from mmisp.util.uuid import uuid


def generate_organisation() -> Organisation:
    return Organisation(
        name=f"unique-{time()}-{uuid()}",
        uuid=uuid(),
        description="auto-generated org",
        type="another free text description",
        nationality="earthian",
        sector="software",
        created_by=0,
        contacts="Test Org\r\nBuilding 42\r\nAdenauerring 7\r\n76131 Karlsruhe\r\nGermany",
        local=True,
        restricted_to_domain="",
        landingpage="",
    )
