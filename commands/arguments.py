"""
This module contains the argument manager class
"""

from argparse import ArgumentParser, Namespace, _ArgumentGroup
from functools import partial
from pathlib import Path
from typing import Any

from deepfake.constants import DEFAULT_CONFIG
from deepfake.commands.cli_options import AVAILABLE_CLI_OPTIONS

ARGS_WEBSERVER: list[str] = []

ARGS_MAIN = ["version_main"]

ARGS_COMMON = [
    "logfile",
    "version",
    "config",
    "datadir",
    "user_data_dir",
]


class Arguments:
    """
    Arguments Class. Manage the arguments received by the cli
    """

    def __init__(self, args: list[str] | None) -> None:
        self.args = args
        self._parsed_arg: Namespace | None = None

    def get_parsed_arg(self) -> dict[str, Any]:
        """
        Return the list of arguments
        :return: List[str] List of arguments
        """
        if self._parsed_arg is None:
            self._build_subcommands()
            self._parsed_arg = self._parse_args()

        return vars(self._parsed_arg)

    def _parse_args(self) -> Namespace:
        """
        Parses given arguments and returns an argparse Namespace instance.
        """
        parsed_arg = self.parser.parse_args(self.args)

        if "config" in parsed_arg and parsed_arg.config is None:
            if "user_data_dir" in parsed_arg and parsed_arg.user_data_dir is not None:
                user_dir = parsed_arg.user_data_dir
            else:
                # Default case
                user_dir = "user_data"
                # Try loading from "user_data/config.json"
            cfgfile = Path(user_dir) / DEFAULT_CONFIG
            if cfgfile.is_file():
                parsed_arg.config = [str(cfgfile)]
            else:
                # Else use "config.json".
                cfgfile = Path.cwd() / DEFAULT_CONFIG
                if cfgfile.is_file():
                    # Only inject config if the file exists, or if the config is required
                    parsed_arg.config = [DEFAULT_CONFIG]

        return parsed_arg

    def _build_args(self, optionlist: list[str], parser: ArgumentParser | _ArgumentGroup) -> None:
        for val in optionlist:
            opt = AVAILABLE_CLI_OPTIONS[val]
            parser.add_argument(*opt.cli, dest=val, **opt.kwargs)

    def _build_subcommands(self) -> None:
        """
        Builds and attaches all subcommands.
        :return: None
        """
        # Build shared arguments (as group Common Options)
        _common_parser = ArgumentParser(add_help=False)
        group = _common_parser.add_argument_group("Common arguments")
        self._build_args(optionlist=ARGS_COMMON, parser=group)

        # Build main command
        self.parser = ArgumentParser(
            prog="deepfake", description="Free, open source crypto trading bot"
        )
        self._build_args(optionlist=ARGS_MAIN, parser=self.parser)

        from deepfake.commands import (
            start_webserver,
        )

        subparsers = self.parser.add_subparsers(
            dest="command",
            # Use custom message when no subhandler is added
            # shown from `main.py`
            # required=True
        )
        
        # Add webserver subcommand
        webserver_cmd = subparsers.add_parser(
            "webserver", help="Webserver module.", parents=[_common_parser]
        )
        webserver_cmd.set_defaults(func=start_webserver)
        self._build_args(optionlist=ARGS_WEBSERVER, parser=webserver_cmd)