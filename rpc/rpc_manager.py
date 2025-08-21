"""
This module contains class to manage RPC communications (Telegram, API, ...)
"""

import logging
from collections import deque

from deepfake.constants import Config
from deepfake.enums import NO_ECHO_MESSAGES, RPCMessageType
from deepfake.rpc import RPC, RPCHandler


logger = logging.getLogger(__name__)


class RPCManager:
    """
    Class to manage RPC objects (Telegram, API, ...)
    """

    def __init__(self, deepfake) -> None:
        """Initializes all enabled rpc modules"""
        self.registered_modules: list[RPCHandler] = []
        self._rpc = RPC(deepfake)
        config = deepfake.config

        # Enable local rest api server for cmd line control
        if config.get("api_server", {}).get("enabled", False):
            logger.info("Enabling rpc.api_server")
            from deepfake.rpc.api_server import ApiServer

            apiserver = ApiServer(config)
            apiserver.add_rpc_handler(self._rpc)
            self.registered_modules.append(apiserver)

    def cleanup(self) -> None:
        """Stops all enabled rpc modules"""
        logger.info("Cleaning up rpc modules ...")
        while self.registered_modules:
            mod = self.registered_modules.pop()
            logger.info("Cleaning up rpc.%s ...", mod.name)
            mod.cleanup()
            del mod

    def send_msg(self, msg) -> None:
        """
        Send given message to all registered rpc modules.
        A message consists of one or more key value pairs of strings.
        e.g.:
        {
            'status': 'stopping bot'
        }
        """
        if msg.get("type") not in NO_ECHO_MESSAGES:
            logger.info("Sending rpc message: %s", msg)
        for mod in self.registered_modules:
            logger.debug("Forwarding message to rpc.%s", mod.name)
            try:
                mod.send_msg(msg)
            except NotImplementedError:
                logger.error(f"Message type '{msg['type']}' not implemented by handler {mod.name}.")
            except Exception:
                logger.exception("Exception occurred within RPC module %s", mod.name)

    def process_msg_queue(self, queue: deque) -> None:
        """
        Process all messages in the queue.
        """
        while queue:
            msg = queue.popleft()
            logger.info("Sending rpc strategy_msg: %s", msg)
            for mod in self.registered_modules:
                if mod._config.get(mod.name, {}).get("allow_custom_messages", False):
                    mod.send_msg(
                        {
                            "type": RPCMessageType.OTHER,
                            "msg": msg,
                        }
                    )
