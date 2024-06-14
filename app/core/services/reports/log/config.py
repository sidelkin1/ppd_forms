import logging
from pathlib import Path


def configure_logging(name: str, path: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    format = (
        "[%(asctime)s] [%(user_id)s - %(request_id)s]"
        " [%(module)s - %(funcName)s] [%(levelname)s] %(message)s"
    )
    log_path = path / "logs.log" if path.is_dir() else path
    datefmt = "%Y-%m-%d %H:%M"
    formatter = logging.Formatter(fmt=format, datefmt=datefmt)
    file_handler = logging.FileHandler(log_path, mode="w", delay=True)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
