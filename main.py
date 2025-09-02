#!/usr/bin/env python3
"""
Main Deepfake bot script.
Read the documentation to know what CLI arguments you need.
"""

import argparse
import logging
import sys

from deepfake import __version__
from deepfake.deepfake import DeepFake, start_create_userdir
from deepfake.exceptions import DeepfakeException
from deepfake.loggers import setup_logging_pre
from deepfake.system import gc_set_threshold, print_version_info

logger = logging.getLogger("deepfake")


def main() -> None:
    """Initiate the DeepFake bot and start the appropriate command."""
    return_code: int = 1

    try:
        setup_logging_pre()
        gc_set_threshold()

        parser = argparse.ArgumentParser(description="DeepFake WebApp Control")
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Define subcommands
        subparsers.add_parser("start", help="Start the web application")
        subparsers.add_parser("train", help="Start training the model")
        subparsers.add_parser("create-userdir", help="Create user-data directory")

        # Global optional flags
        parser.add_argument("--version", "-v", action="store_true", help="Show the version")

        args = parser.parse_args()

        if args.version:
            print_version_info()
            return_code = 0

        else:
            match args.command:
                case "start":
                    deepfake = DeepFake()
                    deepfake.startup()
                    
                case "train":
                    deepfake = DeepFake()
                    deepfake.startup()  
                    
                case "create-userdir":
                    start_create_userdir()

    except SystemExit as e:  # Exiting normally (argparse)
        return_code = e.code
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting...")
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
