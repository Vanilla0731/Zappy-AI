##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## color_formatter
##

import logging

RESET = "\x1b[0m"
BLUE = "\x1b[34m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
BOLD_RED = "\x1b[1;31m"

COLORS = {
    'DEBUG': BLUE,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': BOLD_RED
}

class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_message = super().format(record)
        color = COLORS.get(record.levelname, RESET)
        return f"{color}{log_message}{RESET}"

def init_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    formatter = ColorFormatter('\r%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
