import sys
from loguru import logger


class Log:
    def __init__(self, log_name: str, log_level: str):
        self.log_file = f"{log_name}.log"
        self.log_level = log_level

    def get_logger(self):
        if self.log_level == "DEBUG":
            logger.add(f"{self.log_file}", level="DEBUG", rotation="10 MB", backtrace=True, diagnose=True)
        else:
            logger.remove(0)
            logger.add(sys.stderr, format="<level>{message}</level>", level="INFO", colorize=True)
        return logger
