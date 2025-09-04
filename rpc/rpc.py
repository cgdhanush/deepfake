"""
This module contains class to define a RPC communications
"""

from datetime import datetime
from sqlalchemy.orm import joinedload
import logging
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING
   
from deepfake import __version__
from deepfake.constants import Config
from deepfake.rpc.rpc_types import RPCSendMsg
from deepfake.persistence import Video, Result  # Make sure these are correct paths

logger = logging.getLogger(__name__)


class RPCException(Exception):
    """
    Should be raised with a rpc-formatted message in an _rpc_* method
    if the required state is wrong, i.e.:

    raise RPCException('*Status:* `no active trade`')
    """

    def __init__(self, message: str) -> None:
        super().__init__(self)
        self.message = message

    def __str__(self):
        return self.message

    def __json__(self):
        return {"msg": self.message}


class RPCHandler:
    def __init__(self, rpc: "RPC", config: Config) -> None:
        """
        Initializes RPCHandlers
        :param rpc: instance of RPC Helper class
        :param config: Configuration object
        :return: None
        """
        self._rpc = rpc
        self._config: Config = config

    @property
    def name(self) -> str:
        """Returns the lowercase name of the implementation"""
        return self.__class__.__name__.lower()

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup pending module resources"""

    @abstractmethod
    def send_msg(self, msg: RPCSendMsg) -> None:
        """Sends a message to all registered rpc modules"""


class RPC:
    """
    RPC class can be used to have extra feature, like bot data, and access to DB data
    """
    if TYPE_CHECKING:
        from deepfake.deepfake import DeepFake

        _deepfake: DeepFake

    def __init__(self, deepfake) -> None:
        self._deepfake = deepfake
        self._config = deepfake.config

    def _rpc_deepfakes(self) -> list[Video]:
        """
        Get all stored deepfake video entries
        """
        return (
        Video.session.query(Video)
        .options(joinedload(Video.result))  # Eagerly load the result relationship
        .all()
    )

    def _rpc_add_deepfake(
        self,
        title: str,
        user_id: int,
        description: str,
        duration: str,
        file_path: str,
        uploadedDate: str,
        video_filename: str
    ) -> dict:
        """
        Add a new deepfake video with dummy analysis
        """
        try:
            # Create dummy result
            result = self._rpc_dummy_analysis()

            # Create video object
            video = Video(
                title=title,
                user_id=user_id,
                description=description,
                duration=float(duration),
                file_path=file_path,
                video_filename=video_filename,
                result=result
            )
            
            Video.session.add(video)
            Video.session.commit()

            return {
                "id": video.id,
                "video_filename": video.video_filename, 
            }

        except Exception as e:
            Video.session.rollback()
            raise RuntimeError(f"Failed to add deepfake: {str(e)}")

    def _rpc_delete_deepfake(self, deepfake_id: int) -> bool:
        """
        Delete a deepfake video entry by ID
        """
        try:
            video = Video.session.query(Video).filter_by(id=deepfake_id).first()
            if not video:
                return False

            Video.session.delete(video)  # Result will be deleted via cascade
            Video.session.commit()
            return True

        except Exception as e:
            Video.session.rollback()
            raise RuntimeError(f"Failed to delete deepfake: {str(e)}")

    def _rpc_dummy_analysis(self) -> Result:
        """
        Returns a dummy Result instance
        """
        return Result(
            analysis_model="MockDeepfakeDetector_v1",
            detection_score=0.92,
            deepfake_detected=True,
            confidence="high"
        )
