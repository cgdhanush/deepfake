"""
This module contains the configuration class
"""

import logging
from pathlib import Path
from typing import Any

from deepfake import constants
from deepfake.configuration.load_config import load_file, load_from_files
from deepfake.constants import Config
from deepfake.enums import RunMode

from deepfake.loggers import setup_logging
from deepfake.misc import parse_db_uri_for_logging, safe_value_fallback

logger = logging.getLogger(__name__)


class Configuration:
    """
    Class to read and init the bot configuration
    Reuse this class for the bot, backtesting, hyperopt and every script that required configuration
    """

    def __init__(self, args: dict[str, Any], runmode: RunMode | None = None) -> None:
        self.args = args
        self.config: Config | None = None
        self.runmode = runmode

    def get_config(self) -> Config:
        """
        Return the config. Use this method to get the bot config
        :return: Dict: Bot config
        """
        if self.config is None:
            self.config = self.load_config()

        return self.config

    @staticmethod
    def from_files(files: list[str]) -> dict[str, Any]:
        """
        Iterate through the config files passed in, loading all of them
        and merging their contents.
        Files are loaded in sequence, parameters in later configuration files
        override the same parameter from an earlier file (last definition wins).
        Runs through the whole Configuration initialization, so all expected config entries
        are available to interactive environments.
        :param files: List of file paths
        :return: configuration dictionary
        """
        # Keep this method as staticmethod, so it can be used from interactive environments
        c = Configuration({"config": files}, RunMode.OTHER)
        return c.get_config()

    def load_config(self) -> dict[str, Any]:
        """
        Extract information for sys.argv and load the bot configuration
        :return: Configuration dictionary
        """
        # Load all configs
        config: Config = load_from_files(self.args.get("config", []))

        self._process_logging_options(config)

        self._process_data_options(config)

        self._process_datadir_options(config)

        return config

    def _process_logging_options(self, config: Config) -> None:
        """
        Extract information for sys.argv and load logging configuration:
        the -v/--verbose, --logfile options
        """
        # Log level
        if "verbosity" not in config or self.args.get("verbosity") is not None:
            config.update(
                {"verbosity": safe_value_fallback(self.args, "verbosity", default_value=0)}
            )

        if self.args.get("logfile"):
            config.update({"logfile": self.args["logfile"]})

        if "print_colorized" in self.args and not self.args["print_colorized"]:
            logger.info("Parameter --no-color detected ...")
            config.update({"print_colorized": False})
        else:
            config.update({"print_colorized": True})

        setup_logging(config)

    def _process_data_options(self, config: Config) -> None:
    
        config["db_url"] = constants.DEFAULT_DB_PROD_URL
        logger.info(f'Using DB: "{parse_db_uri_for_logging(config["db_url"])}"')

    def _process_datadir_options(self, config: Config) -> None:
        """
        Extract information for sys.argv and load directory configurations
        --user-data, --datadir
        """
        if self.args.get("user_data_dir"):
            config.update({"user_data_dir": self.args["user_data_dir"]})
        elif "user_data_dir" not in config:
            # Default to cwd/user_data (legacy option ...)
            config.update({"user_data_dir": str(Path.cwd() / "user_data")})