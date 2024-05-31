from datetime import datetime

from mmisp.api_schemas.warninglists import (
    WarninglistCategory,
    WarninglistListType,
)
from mmisp.db.models.warninglist import Warninglist, WarninglistEntry, WarninglistType


def generate_warninglist() -> Warninglist:
    return Warninglist(
        name=f"test warninglist {datetime.utcnow()}",
        type=WarninglistListType.CIDR.value,
        description="test description",
        enabled=True,
        default=False,
        category=WarninglistCategory.KNOWN_IDENTIFIER.value,
    )


def generate_warninglist_entry() -> WarninglistEntry:
    """These fields need to be set manually: warninglist_id"""
    return WarninglistEntry(
        value="test value",
        comment=" test comment",
    )


def generate_warninglist_type() -> WarninglistType:
    """These fields need to be set manually: warninglist_id"""
    return WarninglistType(type="md5")
