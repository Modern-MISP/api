from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from ..database import Base


class UserSettings(Base):
    id = Column(String)
    setting = Column(String)
    user_id = Column(String)
    timestamp = Column(String)
    widget = Column(String)
    position = relationship("UserSettingsPosition", backref="UserSettings")
    value = relationship("UserSettingsPosition", backref="UserSettings")


class UserSettingsValue(Base):
    widget = Column(String)
    position = relationship("UserSettingsPosition", backref="UserSettingsValue")


class UserSettingsPosition(Base):
    x = Column(String)
    y = Column(String)
    width = Column(String)
    height = Column(String)
