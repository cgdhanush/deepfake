"""
This module contains the class to persist Videos into SQLite
"""

import logging
from typing import Any, ClassVar

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from deepfake.persistence.base import ModelBase, SessionType

logger = logging.getLogger(__name__)

# Association table for many-to-many relationship between videos and users
video_user_association = Table(
    "video_user_association",
    ModelBase.metadata,
    Column("video_id", ForeignKey("videos.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Users(ModelBase):
    """
    Users database model
    Keeps a record of all users placed on the exchange
    """

    __tablename__ = "users"
    __allow_unmapped__ = True
    session: ClassVar[SessionType]

    __table_args__ = (UniqueConstraint("id", name="_user_id_uc"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self):
        return f"Users(id={self.id})"


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

    users: Mapped[list[Users]] = relationship(
        "Users",
        secondary=video_user_association,
        order_by="Users.id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, **kwargs):
        LocalVideo.__init__(self, **kwargs)

    def __repr__(self):
        return f"Video(id={self.id}, users={self.users})"

    @staticmethod
    def commit():
        Video.session.commit()

    @staticmethod
    def rollback():
        Video.session.rollback()
