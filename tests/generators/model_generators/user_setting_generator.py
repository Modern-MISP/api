import json
from time import time

from mmisp.db.models.user_setting import SettingName, UserSetting


def generate_user_setting() -> UserSetting:
    """These fields need to be set manually: user_id"""
    return UserSetting(
        setting=SettingName.PUBLISH_ALERT_FILTER.value,
        value=json.dumps({"attribute": str(time())}),
    )


def generate_user_name() -> UserSetting:
    """These fields need to be set manually: user_id"""
    return UserSetting(
        setting=SettingName.USER_NAME.value,
        value=json.dumps({"name": "generated-user" + str(time())}),
    )
