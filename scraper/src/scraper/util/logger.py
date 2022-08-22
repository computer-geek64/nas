# logger.py
import sys
import logging
from ..config import config


def init_logger(name: str) -> logging.Logger:
    formatter = logging.Formatter('{asctime}.{msecs:03.0f} [{levelname}] {name} - {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if 'STDOUT' in config['LOG']:
        stdout_log_handler = logging.StreamHandler(sys.stdout)
        stdout_log_handler.setFormatter(formatter)
        stdout_log_handler.setLevel(getattr(logging, config['LOG']['STDOUT']))

    if 'STDERR' in config['LOG']:
        stderr_log_handler = logging.StreamHandler(sys.stderr)
        stderr_log_handler.setFormatter(formatter)
        stderr_log_handler.setLevel(getattr(logging, config['LOG']['STDERR']))
        logger.addHandler(stderr_log_handler)

    for log_file in config['LOG']['FILES']:
        log_file_handler = logging.FileHandler(log_file['FILENAME'], mode=log_file['MODE'])
        log_file_handler.setLevel(getattr(logging, log_file['LEVEL']))
        logger.addHandler(log_file_handler)

    return logger
