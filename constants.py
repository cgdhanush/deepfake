from typing import Any

DEFAULT_CONFIG = "config.json"
DEFAULT_DB_PROD_URL = "sqlite:///user_data/datav3.sqlite"
DEFAULT_LOG_FILE = "deepfake.log"

DATETIME_PRINT_FORMAT = "%Y-%m-%d %H:%M:%S"

USER_DATA_DIR = "user_data"
DATA_DIR = "data_dir"
UPLOAD_DIR = "upload_dir"

Config = dict[str, Any]
