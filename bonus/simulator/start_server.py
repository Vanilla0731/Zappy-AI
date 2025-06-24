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
from .file_mgmt import get_log_path, strip_ansi

SERVER_ENV = {
    "SERVER_PATH": getenv("SERVER_PATH"),
    "SERVER_ARGS": getenv("SERVER_ARGS")
}

UNINITIALIZED_VARS = [k for k, v in SERVER_ENV.items() if v is None]

if UNINITIALIZED_VARS:
    raise SimError("start_server", f"The following environment variables should be initialized but they are not: {UNINITIALIZED_VARS}")

logger.debug(f"SERVER COMMAND: {SERVER_ENV.get("SERVER_PATH")} {SERVER_ENV.get("SERVER_ARGS")}")

tmp = getenv("SHOULD_QUIT_ON_FULL_TEAM")

try:
    should_quit = bool(int(tmp)) if tmp else False
except ValueError:
    should_quit = False

process = None

logger.debug(f"USING SHOULD_QUIT_ON_FULL_TEAM={should_quit}")

def start_server():
    log_path = get_log_path("server")

    try:
        with open(log_path, "w") as logfile:
            process = subprocess.Popen(
                ["valgrind", SERVER_ENV.get("SERVER_PATH")] + SERVER_ENV.get("SERVER_ARGS", "").split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            if should_quit:
                for line in process.stdout:
                    clean_line = strip_ansi(line)
                    logfile.write(clean_line)
                    logfile.flush()
                    if "Client" in line and "tried to join full team" in line:
                        logger.info("Detected full team join attempt — sending SIGINT.")
                        process.send_signal(SIGINT)
                        break

        process.wait()
    except Exception as e:
        logger.error("Error during server monitoring:", e)
    finally:
        if process and process.poll() is None:
            process.terminate()
