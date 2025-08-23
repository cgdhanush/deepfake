"""
The Main class
"""

import logging

from deepfake.constants import Config
from deepfake.configuration import Configuration
from deepfake.mixins import LoggingMixin
from deepfake.persistence import Video, LocalVideo, Users, init_db
from deepfake.misc import load_json

logger = logging.getLogger(__name__)

class DeepFake(LoggingMixin):

    def __init__(self):
    
        self.config: Config = Configuration().get_config()

        init_db(self.config["db_url"])

        LoggingMixin.__init__(self, logger)

    def startup(self,):
        print("Starting Up...")
        print(self.config)