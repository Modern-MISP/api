from mmisp.db.models.tag import Tag
from mmisp.util.uuid import uuid


def generate_tag() -> Tag:
    """These fields need to be set manually: org_id, user_id"""
    return Tag(
        name=f"test tag {uuid()}",
        colour="#123456",
        exportable=False,
        hide_tag=False,
        numerical_value=1,
        inherited=False,
    )
