import contextlib
import sys
from pathlib import Path
from loguru import logger


class Log:
    def __init__(self, log_name: str, log_level: str):
        self.log_file = f"{Path(__file__).parent.parent.parent / 'logs' / f'{log_name}.log'}"
        self.log_level = log_level

    def get_logger(self):
        logger.remove()

        # Add custom log level
        with contextlib.suppress(TypeError):
            logger.level("CUSTOM", no=38, color="<green>", icon="🐍")
            # Add level with no:100 for printing
            logger.level("PRINT", no=100, color="<white>", icon="ℹ️")

        if self.log_level == "DEBUG":
            logger_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
            logger.add(sys.stderr, format=logger_format, level="DEBUG", backtrace=True, diagnose=True,
                       filter=self._filter_out_custom_logs())
        else:
            logger_format = "<level>{message}</level>"

            # Add custom logger format if log level is custom
            if self.log_level == "CUSTOM":
                logger_format = f"{{level.icon}} {logger_format}"
                logger.add(sys.stderr, format=logger_format, level=self.log_level, colorize=True)
            else:
                logger.add(sys.stderr, format=logger_format, level=self.log_level, colorize=True,
                           filter=self._filter_out_custom_logs())

        # Always log debug info to file
        logger.add(f"{self.log_file}", level="DEBUG", rotation="10 MB", backtrace=True, diagnose=True,
                   filter=self._filter_out_custom_logs())
        return logger

    @staticmethod
    def _filter_out_custom_logs():
        return lambda record: record["level"].name != "CUSTOM"
