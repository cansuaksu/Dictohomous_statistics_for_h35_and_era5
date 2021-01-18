import logging

logging.basicConfig(level=logging.INFO)


class Logger:
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)

        self.formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.stream_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.stream_handler)

    def log_debug(self, text):
        self.logger.debug(text)

    def log_info(self, text):
        self.logger.info(text)

    def log_warning(self, text):
        self.logger.warning(text)

    def log_error(self, text):
        self.logger.error(text)

    def log_critical(self, text):
        self.logger.critical(text)
