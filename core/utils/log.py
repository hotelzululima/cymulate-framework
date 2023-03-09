from loguru import logger


class Log:
    def __init__(self, log_name, log_level):
        self.log_name = log_name
        self.log_level = log_level

    def get_logger(self):
        logger.add(f"{self.log_name}", level=self.log_level, rotation="5 MB")
        return logger
