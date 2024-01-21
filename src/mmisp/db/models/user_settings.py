from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    setting = Column(String)
    user_id = Column(String)
    timestamp = Column(String)
    widget = Column(String)
    position = relationship("UserSettingsPosition", backref="UserSettings")
    value = relationship("UserSettingsPosition", backref="UserSettings")


class UserSettingsValue(Base):
    __tablename__ = "user_settings_values"

    id = Column(Integer, primary_key=True)
    widget = Column(String)
    position = relationship("UserSettingsPosition", backref="UserSettingsValue")


class UserSettingsPosition(Base):
    __tablename__ = "user_settings_positions"

    id = Column(Integer, primary_key=True)
    x = Column(String)
    y = Column(String)
    width = Column(String)
    height = Column(String)
