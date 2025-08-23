"""
This module contains class to define a RPC communications
"""

import logging
from abc import abstractmethod

from deepfake import __version__
from deepfake.constants import  Config
from deepfake.rpc.rpc_types import RPCSendMsg

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

    def __init__(self, deepfake) -> None:
        """
        Initializes all enabled rpc modules
        :param deepfake: Instance of a deepfake bot
        :return: None
        """
        self._deepfake = deepfake
        self._config: Config = deepfake.config
        
   