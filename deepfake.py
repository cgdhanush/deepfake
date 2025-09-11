"""
The Main class
"""

import logging
from typing import Any, Dict
from argparse import ArgumentParser, Namespace

from deepfake.constants import Config
from deepfake.configuration import Configuration
from deepfake.persistence import init_db

logger = logging.getLogger(__name__)


class DeepFake:
    """
    Main Class
    """
    def __init__(self):
        self.config: Config = Configuration().get_config()
        init_db(self.config["db_url"])

    def startup(self) -> None:
        """
        Start the Webserver to test.
        """
        from deepfake.rpc.api_server.webserver import ApiServer
        from deepfake.rpc import RPC
        
        # Start the Websrver
        self._api_server = ApiServer(self.config)
        self._rpc = RPC(self)
        
        self._api_server.add_rpc_handler(self._rpc)
        
    def start_train(self) -> None:
        """"
        strat the training model...
        """
        print(self.config)
    
    def start_predict(self) -> None:
        from deepfake.deepfakeai.lib import extract_frames
        extract_frames(self.config)


class Arguments:
    """
    Handles command-line arguments parsing.
    """
    def __init__(self, argv: list[str]):
        self.argv = argv
        self.parser = ArgumentParser(
            description="DeepFake WebApp Control"
        )
        self._add_arguments()
        self.parsed_args = self._parse_args()

    def _add_arguments(self) -> None:
        self.parser.add_argument(
            "-v", "--version", 
            dest="version_main", 
            action="store_true", 
            help="Show version and exit"
        )

        # Create subparsers, but don't require them *yet*
        self.subparsers = self.parser.add_subparsers(dest="command")  # ← No required=True

        self.subparsers.add_parser("start", help="Start the web application")
        self.subparsers.add_parser("train", help="Start training the model")
        self.subparsers.add_parser("predict", help="Start Predict the Video")
        self.subparsers.add_parser("create-userdir", help="Create user-data directory")

    def _parse_args(self) -> Namespace:
        args = self.parser.parse_args(self.argv)

        # Only enforce subcommand if version was not requested
        if not args.version_main and args.command is None:
            self.parser.error("a subcommand is required: {start, train, create-userdir}")

        return args

    def get_parsed_arg(self) -> Dict[str, Any]:
        return vars(self.parsed_args)

def start_create_userdir() -> None:
    """
    Create "user_data" directory to contain user data.
    """
    from deepfake.configuration.directory_operations import (
        create_userdata_dir,
        copy_sample_files
    )
    from deepfake.constants import USER_DATA_DIR
    
    user_dir = create_userdata_dir(USER_DATA_DIR, create_dir=True)
    copy_sample_files(user_dir)