import logging
import os

LOG_FILE = os.path.expanduser('~/.config/e-zshot/e-zshot.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logging() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_message(message: str) -> None:
    logging.info(message)
