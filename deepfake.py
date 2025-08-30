"""
The Main class
"""

import logging

from deepfake.constants import Config
from deepfake.configuration import Configuration
from deepfake.persistence import Video, LocalVideo, init_db

logger = logging.getLogger(__name__)

class DeepFake:

    def __init__(self):
    
        self.config: Config = Configuration().get_config()

        init_db(self.config["db_url"])

    def startup(self):
        
        from deepfake.api_server import ApiServer
        ApiServer(self.config, standalone=True)
