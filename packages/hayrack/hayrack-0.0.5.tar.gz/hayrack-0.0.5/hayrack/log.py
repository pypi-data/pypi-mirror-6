import logging


def configure_logging(cfg):
    """
    Initialize the root logger from a HayrackConfiguration object
    """
    logger = logging.getLogger()
    logger.setLevel(cfg.logging.verbosity)
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                                  "%Y-%m-%d %H:%M:%S")

    if cfg.logging.logfile:
        file_handler = logging.FileHandler(cfg.logging.logfile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if bool(cfg.logging.console):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(logging.StreamHandler())
