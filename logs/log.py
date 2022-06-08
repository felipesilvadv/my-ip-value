import logging

FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"

def getLogger(name, set_stream_format=True):
    logger = logging.getLogger(name)
    if set_stream_format:
        fmt = logging.Formatter(FORMAT)
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger