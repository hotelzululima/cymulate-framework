import sys
from pathlib import Path
from loguru import logger


class Log:
    def __init__(self, log_name: str, log_level: str):
        self.log_file = f"{Path(__file__).parent.parent.parent / 'logs' / f'{log_name}.log'}"
        self.log_level = log_level

    def get_logger(self):
        if self.log_level != 'DEBUG':
            logger.remove()
            logger.add(sys.stderr, format="<level>{message}</level>", level=self.log_level, colorize=True)
        logger.add(f"{self.log_file}", level="DEBUG", rotation="10 MB", backtrace=True, diagnose=True)
        return logger
