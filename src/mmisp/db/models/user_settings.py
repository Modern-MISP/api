from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    setting = Column(String(255))
    user_id = Column(String(255))
    timestamp = Column(String(255))
    widget = Column(String(255))
    position = relationship("UserSettingsPosition", backref="UserSettings")
    value = relationship("UserSettingsPosition", backref="UserSettings")


class UserSettingsValue(Base):
    __tablename__ = "user_settings_values"

    id = Column(Integer, primary_key=True)
    widget = Column(String(255))
    position = relationship("UserSettingsPosition", backref="UserSettingsValue")


class UserSettingsPosition(Base):
    __tablename__ = "user_settings_positions"

    id = Column(Integer, primary_key=True)
    x = Column(String(255))
    y = Column(String(255))
    width = Column(String(255))
    height = Column(String(255))
