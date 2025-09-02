"""
The Main class
"""

import logging
import sys
from typing import Any

from deepfake.constants import Config
from deepfake.configuration import Configuration
from deepfake.persistence import Video, LocalVideo, init_db

logger = logging.getLogger(__name__)


class DeepFake:

    def __init__(self):
    
        self.config: Config = Configuration().get_config()

        init_db(self.config["db_url"])

    def startup(self) -> None:
        """
        Start the Webserver to test.
        """
        from deepfake.rpc.api_server import ApiServer
        from deepfake.rpc import RPC
        
        # Start the Websrver
        self._api_server = ApiServer(self.config)
        self._rpc = RPC(self)
        
        self._api_server.add_rpc_handler(self._rpc)
        
    def start_train(self) -> None:
        """"
        strat the training model...
        """
        pass
    

def start_create_userdir() -> None:
    """
    Create "user_data" directory to contain user data.
    """
    from deepfake.configuration.directory_operations import create_userdata_dir, copy_sample_files
    from deepfake.constants import USER_DATA_DIR
    
    user_dir = create_userdata_dir(USER_DATA_DIR, create_dir=True)
    copy_sample_files(user_dir)