from mmisp.db.models.sharing_group import SharingGroup


def generate_sharing_group() -> SharingGroup:
    """These fields need to be set manually: organisation_uuid, org_id, [sync_user_id]"""
    return SharingGroup(
        name="Test Sharing Group",
        description="This is a description field",
        releasability="this is yet another description field",
        sync_user_id=0,
    )
