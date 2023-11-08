import logging

def get_logger(name: str):
    # Configures and returns a logger instance

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
