"""
This module contains the class to persist Videos into SQLite
"""

import logging
from typing import Any, ClassVar

from sqlalchemy import Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from deepfake.persistence.base import ModelBase, SessionType

logger = logging.getLogger(__name__)


class LocalVideo:
    """
    A base local video class for handling video data before persistence
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 0)
        self.users = kwargs.get("users", [])

    def __repr__(self):
        return f"Video(id={self.id})"


class Video(ModelBase, LocalVideo):
    """
    Video model to persist video information
    """

    __tablename__ = "videos"
    session: ClassVar[SessionType]

    use_db: bool = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __init__(self, **kwargs):
        LocalVideo.__init__(self, **kwargs)

    def __repr__(self):
        return f"Video(id={self.id})"

    @staticmethod
    def commit():
        Video.session.commit()

    @staticmethod
    def rollback():
        Video.session.rollback()
