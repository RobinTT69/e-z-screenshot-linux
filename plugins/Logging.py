import logging

def log_message(level: int, message: str) -> None:
    """Log a message with the appropriate severity."""
    log_func = {
        logging.DEBUG: logging.debug,
        logging.INFO: logging.info,
        logging.WARNING: logging.warning,
        logging.ERROR: logging.error,
        logging.CRITICAL: logging.critical
    }.get(level, logging.info)
    log_func(message)

