from time import time
from uuid import uuid4

from mmisp.db.models.sharing_group import SharingGroup


def generate_sharing_group() -> SharingGroup:
    """These fields need to be set manually: organisation_uuid, org_id, [sync_user_id]"""
    return SharingGroup(
        name=f"unique-{int(time())}-{uuid4().hex}",
        description="This is a description field",
        releasability="this is yet another description field",
        sync_user_id=0,
        active=False,
        local=True,
    )
