import logging


def setup_logging(level=logging.INFO) -> logging.Logger:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=level,
    )
    logger = logging.getLogger("bot")
    logger.setLevel(level)
    return logger
