import logging

logger = logging.getLogger("FA")

def ConfigureLogger(level):
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s %(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)