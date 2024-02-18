from enum import Enum
from time import time

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from mmisp.db.database import Base

from .user import User


class SettingName(Enum):
    PUBLISH_ALERT_FILTER = "publish_alert_filter"
    DASHBOARD_ACCESS = "dashboard_access"
    DASHBOARD = "dashboard"
    HOMEPAGE = "homepage"
    DEFAULT_RESTSEARCH_PARAMETERS = "default_restsearch_parameters"
    TAG_NUMERICAL_VALUE_OVERRIDE = "tag_numerical_value_override"
    EVENT_INDEX_HIDE_COLUMNS = "event_index_hide_columns"
    PERIODIC_NOTIFICATION_FILTERS = "periodic_notification_filters"


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    setting = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    value = Column(Text)
    timestamp = Column(Integer, default=time, onupdate=time)

    user = relationship(User, primaryjoin=user_id == User.id)
