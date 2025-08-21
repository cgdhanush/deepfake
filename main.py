#!/usr/bin/env python3
"""
Main Deepfake bot script.
Read the documentation to know what cli arguments you need.
"""

import logging
import sys
from typing import Any


# check min. python version
if sys.version_info < (3, 11):  # pragma: no cover  # noqa: UP036
    sys.exit("Deepfake requires Python version >= 3.11")

from deepfake import __version__
from deepfake.commands import Arguments
from deepfake.exceptions import ConfigurationError, DeepfakeException, OperationalException
from deepfake.loggers import setup_logging_pre
from deepfake.system import  gc_set_threshold, print_version_info


logger = logging.getLogger("deepfake")


def main(sysargv: list[str] | None = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    return_code: Any = 1
    try:
        setup_logging_pre()
        arguments = Arguments(sysargv)
        args = arguments.get_parsed_arg()

        # Call subcommand.
        if args.get("version") or args.get("version_main"):
            print_version_info()
            return_code = 0
        elif "func" in args:
            logger.info(f"deepfake {__version__}")
            gc_set_threshold()
            return_code = args["func"](args)
        else:
            # No subcommand was issued.
            raise OperationalException(
                "Usage of Deepfake requires a subcommand to be specified.\n"
                "To have the bot executing trades in live/dry-run modes, "
                "depending on the value of the `dry_run` setting in the config, run Deepfake "
                "as `deepfake trade [options...]`.\n"
                "To see the full list of options available, please use "
                "`deepfake --help` or `deepfake <command> --help`."
            )

    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
        return_code = 0
    except ConfigurationError as e:
        logger.error(
            f"Configuration error: {e}\n"
            f"Please make sure to review the documentation."
        )
    except DeepfakeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception("Fatal exception!")
    finally:
        sys.exit(return_code)


if __name__ == "__main__":  # pragma: no cover
    main()
