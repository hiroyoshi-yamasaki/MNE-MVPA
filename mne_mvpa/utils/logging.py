import logging
import os
from pathlib import Path

import mne

from ..definitions import ROOT_DIR


def get_log_dir() -> Path:

    path = ROOT_DIR / "logs"  # /MNE-MVPA/logs
    log_dir = Path(path)

    return log_dir


def setup_logging(name: str, level: str, mne_level: str) -> logging.Logger:
    """
    Set up and return a logger
    :param name: name of the log file
    :param level: logging level
    :param mne_level: log level for the MNE-python functions
    :return:
        Logger
    """

    logger = logging.getLogger(name)

    # Set logging level
    if level == "debug":
        logger.setLevel(logging.DEBUG)
    elif level == "info":
        logger.setLevel(logging.INFO)
    elif level == "warning":
        logger.setLevel(logging.WARNING)
    elif level == "error":
        logger.setLevel(logging.ERROR)
    elif level == "critical":
        logger.setLevel(logging.CRITICAL)
    else:
        raise ValueError(f"Unknown logging level {level}")

    log_dir = get_log_dir()

    # In multithreading other thread may have already done this
    try:
        if not log_dir.exists():
            os.makedirs(log_dir)
    except FileExistsError:
        pass

    # Setup handlers
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_dir / f"{name}.log")
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Setup formatters
    fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
          "%(funcName)s() :: Line %(lineno)d :: %(message)s"
    formatter = logging.Formatter(fmt)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(logging.Formatter(""))

    # Add handlers
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # Update MNE settings
    mne.set_log_file(log_dir / f"{name}.log", overwrite=False)
    mne.set_log_level(mne_level)

    return logger
