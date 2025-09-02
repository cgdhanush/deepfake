import logging
import shutil
from pathlib import Path

from deepfake.constants import Config
from deepfake.exceptions import OperationalException


logger = logging.getLogger(__name__)


def create_datadir(config: dict, datadir: str | None = None) -> Path:
    # Determine the base data folder
    folder = Path(datadir) if datadir else Path(f"{config['user_data_dir']}/data")
    
    # Create the main data directory if it doesn't exist
    if not folder.is_dir():
        folder.mkdir(parents=True)
        logger.info(f"Created data directory: {folder}")

    # Create 'real' and 'fake' subdirectories
    real_dir = folder / "real"
    fake_dir = folder / "fake"

    for subfolder in [real_dir, fake_dir]:
        if not subfolder.is_dir():
            subfolder.mkdir(parents=True)
            logger.info(f"Created subdirectory: {subfolder}")

    return folder


def create_userdata_dir(directory: str, create_dir: bool = False) -> Path:
    sub_dirs = [
        "results",
        "data",
        "uploads",
        "logs",
    ]
    folder = Path(directory)

    if not folder.is_dir():
        if create_dir:
            folder.mkdir(parents=True)
            logger.info(f"Created user-data directory: {folder}")
        else:
            raise OperationalException(
                f"Directory `{folder}` does not exist. "
                "Please use `deepfake create-userdir` to create a user directory"
            )

    # Create required subdirectories
    for f in sub_dirs:
        subfolder = folder / f
        if not subfolder.is_dir():
            if subfolder.exists() or subfolder.is_symlink():
                raise OperationalException(
                    f"File `{subfolder}` exists already and is not a directory. "
                    "Freqtrade requires this to be a directory."
                )
            subfolder.mkdir(parents=False)
    return folder
