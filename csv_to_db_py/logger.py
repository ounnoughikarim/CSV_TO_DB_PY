import logging
from rich.logging import RichHandler


def set_logger(level: str):
    logging.basicConfig(
        format="%(message)s",
        level=level.upper(),
        handlers=[RichHandler()],
    )
    logger = logging.getLogger()
    return logger


def get_logger():
    return logging.getLogger(__name__)


logger = get_logger()
