from sqlalchemy import Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import ClassVar, Optional

from deepfake.persistence.base import ModelBase, SessionType
import logging

logger = logging.getLogger(__name__)


class User(ModelBase):
    __tablename__ = "users"
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # One user can have many videos
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"


class LocalVideo:
    id: int
    title: str
    description: Optional[str]
    duration: Optional[float]
    file_path: Optional[str]
    uploadedDate: Optional[datetime]
    video_filename: Optional[str]
    result: Optional["Result"]

    def __repr__(self):
        return f"Video(id={self.id}, title={self.title})"

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Video(ModelBase, LocalVideo):
    __tablename__ = "videos"
    session: ClassVar[SessionType]
    use_db: bool = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    duration: Mapped[Optional[float]] = mapped_column(Float)
    file_path: Mapped[Optional[str]] = mapped_column(String)
    uploadedDate: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.now)
    video_filename: Mapped[Optional[str]] = mapped_column(String)

    # Foreign key to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Many videos belong to one user
    user: Mapped["User"] = relationship("User", back_populates="videos")

    # One-to-one relationship
    result: Mapped[Optional["Result"]] = relationship("Result", back_populates="video", uselist=False, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"Video(id={self.id}, title={self.title})"

    @staticmethod
    def commit():
        Video.session.commit()

    @staticmethod
    def rollback():
        Video.session.rollback()


class Result(ModelBase):
    __tablename__ = "results"
    session: ClassVar[SessionType]

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"), unique=True)
    analysis_model: Mapped[str] = mapped_column(String)
    detection_score: Mapped[float] = mapped_column(Float)
    deepfake_detected: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[str] = mapped_column(String)

    # Back-reference to Video
    video: Mapped["Video"] = relationship("Video", back_populates="result")

    def __repr__(self):
        return f"Result(model={self.analysis_model}, score={self.detection_score}, detected={self.deepfake_detected})"
