##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## start_AI
##

import re
from uuid import uuid4
from os import path, makedirs

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def get_log_path(src: str) -> str:
    log_dir = path.join(path.dirname(path.abspath(__file__)), "logs")
    makedirs(log_dir, exist_ok=True)

    log_path = ""

    while True:
        log_filename = f"{src}_log_{uuid4().hex}.log"
        log_path = path.join(log_dir, log_filename)
        if not path.exists(log_path):
            break

    return log_path

def strip_ansi(line):
    return ANSI_ESCAPE.sub('', line)
