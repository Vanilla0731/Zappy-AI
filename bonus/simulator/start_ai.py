##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## start_AI
##

import subprocess
from uuid import uuid4
from .exception import SimError
from os import getenv, path, makedirs

AI_ENV = {
    "AI_PATH": getenv("AI_PATH"),
    "AI_ARGS": getenv("AI_ARGS")
}

UNINITIALIZED_VARS = [k for k, v in AI_ENV.items() if v is None]

if UNINITIALIZED_VARS:
    raise SimError("start_ai", f"The following environment variables should be initialized but they are not: {UNINITIALIZED_VARS}")

def get_log_path() -> str:
    log_dir = path.join(path.dirname(path.abspath(__file__)), "logs")
    makedirs(log_dir, exist_ok=True)

    log_path = ""

    while True:
        log_filename = f"ai_log_{uuid4().hex}.log"
        log_path = path.join(log_dir, log_filename)
        if not path.exists(log_path):
            break

    return log_path

def start_ai():
    log_path = get_log_path()

    with open(log_path, "w") as logfile:
        process = subprocess.Popen(
            [AI_ENV.get("AI_PATH")] + AI_ENV.get("AI_ARGS", "").split(' '),
            stdout=logfile,
            stderr=logfile
        )
        process.wait()
