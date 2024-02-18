import json

from mmisp.db.models.noticelist import Noticelist, NoticelistEntry


def generate_random_noticelist_input() -> Noticelist:
    return Noticelist(
        name="Test Noticelist",
        expanded_name="Test more noticelist",
        ref=json.dumps("this is a reference"),
        geographical_area=json.dumps("EU"),
        version=1,
        # At creation always on true for TestToggleEnableNoticelist
        enabled=True,
    )


def generate_noticelistentry() -> NoticelistEntry:
    """These fields need to be set manually: noticelist_id"""
    return NoticelistEntry(
        scope=json.dumps("these are the scopes"),
        field=json.dumps("these are the fields"),
        value=json.dumps("these are the values"),
        tags=json.dumps("these are the tags"),
        message="this is a message",
    )
