"""
Definition of cli arguments used in arguments.py
"""

from argparse import SUPPRESS, ArgumentTypeError

from deepfake import constants


def check_int_positive(value: str) -> int:
    try:
        uint = int(value)
        if uint <= 0:
            raise ValueError
    except ValueError:
        raise ArgumentTypeError(
            f"{value} is invalid for this parameter, should be a positive integer value"
        )
    return uint


def check_int_nonzero(value: str) -> int:
    try:
        uint = int(value)
        if uint == 0:
            raise ValueError
    except ValueError:
        raise ArgumentTypeError(
            f"{value} is invalid for this parameter, should be a non-zero integer value"
        )
    return uint


class Arg:
    # Optional CLI arguments
    def __init__(self, *args, **kwargs):
        self.cli = args
        self.kwargs = kwargs


# List of available command line options
AVAILABLE_CLI_OPTIONS = {
    # Common options
    "verbosity": Arg(
        "-v",
        "--verbose",
        help="Verbose mode (-vv for more, -vvv to get all messages).",
        action="count",
    ),
    "logfile": Arg(
        "--logfile",
        "--log-file",
        help="Log to the file specified. Special values are: 'syslog', 'journald'. "
        "See the documentation for more details.",
        metavar="FILE",
    ),
    "version": Arg(
        "-V",
        "--version",
        help="show program's version number and exit",
        action="store_true",
    ),
    "version_main": Arg(
        # Copy of version - used to have -V available with and without subcommand.
        "-V",
        "--version",
        help="show program's version number and exit",
        action="store_true",
    ),
    "config": Arg(
        "-c",
        "--config",
        help=f"Specify configuration file (default: `userdir/{constants.DEFAULT_CONFIG}` "
        f"or `config.json` whichever exists). "
        f"Multiple --config options may be used. "
        f"Can be set to `-` to read config from stdin.",
        action="append",
        metavar="PATH",
    ),
    "datadir": Arg(
        "-d",
        "--datadir",
        "--data-dir",
        help="Path to the base directory of the exchange with historical backtesting data. "
        "To see futures data, use trading-mode additionally.",
        metavar="PATH",
    ),
    "user_data_dir": Arg(
        "--userdir",
        "--user-data-dir",
        help="Path to userdata directory.",
        metavar="PATH",
    ),
    "reset": Arg(
        "--reset",
        help="Reset sample files to their original state.",
        action="store_true",
    )
}
