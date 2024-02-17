from mmisp.db.models.warninglist import Warninglist, WarninglistEntry


def generate_warninglist() -> Warninglist:
    return Warninglist(
        name="test warning list",
        type="test type",
        description="test description",
        version=1,
        enabled=True,
        default=False,
        category="test category",
        warninglist_entry_count=0,
        valid_attributes="test attributes",
    )


def generate_warninglist_entry() -> WarninglistEntry:
    """These fields need to be set manually: warninglist_id"""
    return WarninglistEntry(
        value="test value",
        comment=" test comment",
    )
