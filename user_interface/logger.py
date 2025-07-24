import logging

logger = logging.getLogger("FA")

class CustomFormatter(logging.Formatter):
    grey = "\x1b[0;37m"
    green = "\x1b[1;32m"
    yellow = "\x1b[1;33m"
    red = "\x1b[1;31m"
    purple = "\x1b[1;35m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    reset = "\x1b[0m"
    blink_red = "\x1b[5m\x1b[1;31m"

    format = "%(levelname)s %(asctime)s - %(message)s"

    colorized_formats = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: blink_red + format + reset
    }

    def format(self, record):
        colorized_format = self.colorized_formats.get(record.levelno)
        formatter = logging.Formatter(colorized_format)
        return formatter.format(record)

def ConfigureLogger(level):
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)