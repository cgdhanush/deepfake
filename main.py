#!/usr/bin/env python3
"""
Main Deepfake bot script.
Read the documentation to know what cli arguments you need.
"""

import logging
import sys
from typing import Any

import argparse
from deepfake import __version__
from deepfake.exceptions import DeepfakeException
from deepfake.loggers import setup_logging_pre
from deepfake.system import  gc_set_threshold, print_version_info


logger = logging.getLogger("deepfake")


def main() -> None:
    """
    This function will initiate the bot and start the loop.
    :return: None
    """

    return_code: Any = 1
    try:
        setup_logging_pre()
        gc_set_threshold()

        parser = argparse.ArgumentParser(description="Deepfake CLI")

        # Mutually exclusive group so only one action can be used at a time
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument("start", action="store_true", help="Start the webpage")
        group.add_argument("--version", "-v", action="store_true", help="Show the version")

        args = parser.parse_args()

        if args.start:
            print("starting")

        if args.version:
           print_version_info()

        # Call subcommand.
    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
        return_code = 0
    except DeepfakeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception("Fatal exception!")
    finally:
        sys.exit(return_code)


if __name__ == "__main__":  # pragma: no cover
    main()
