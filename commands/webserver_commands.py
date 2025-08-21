from typing import Any

from deepfake.enums import RunMode


def start_webserver(args: dict[str, Any]) -> None:
    """
    Main entry point for webserver mode
    """
    from deepfake.configuration import setup_utils_configuration
    from deepfake.rpc.api_server import ApiServer

    # Initialize configuration

    config = setup_utils_configuration(args, RunMode.WEBSERVER)
    print(config)
    ApiServer(config, standalone=True)
