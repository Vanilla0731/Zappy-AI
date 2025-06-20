##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## start_server
##

import subprocess
from . import logger
from os import getenv
from signal import SIGINT
from .exception import SimError

SERVER_ENV = {
    "SERVER_PATH": getenv("SERVER_PATH"),
    "SERVER_ARGS": getenv("SERVER_ARGS")
}

UNINITIALIZED_VARS = [k for k, v in SERVER_ENV.items() if v is None]

if UNINITIALIZED_VARS:
    raise SimError("start_server", f"The following environment variables should be initialized but they are not: {UNINITIALIZED_VARS}")

def start_server():
    process = subprocess.Popen(
        [SERVER_ENV.get("SERVER_PATH")] + SERVER_ENV.get("SERVER_ARGS", "").split(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        for line in process.stderr:
            if "Client" in line and "tried to join full team" in line:
                logger.info("Detected full team join attempt — sending SIGINT.")
                process.send_signal(SIGINT)
                break

        process.wait()
    except Exception as e:
        logger.error("Error during server monitoring:", e)
    finally:
        if process.poll() is None:
            process.terminate()
