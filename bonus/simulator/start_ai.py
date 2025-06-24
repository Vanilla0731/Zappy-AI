##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## start_AI
##

import subprocess
from . import logger
from os import getenv
from .exception import SimError
from .file_mgmt import get_log_path, strip_ansi


AI_ENV = {
    "AI_PATH": getenv("AI_PATH"),
    "AI_ARGS": getenv("AI_ARGS")
}

UNINITIALIZED_VARS = [k for k, v in AI_ENV.items() if v is None]

if UNINITIALIZED_VARS:
    raise SimError("start_ai", f"The following environment variables should be initialized but they are not: {UNINITIALIZED_VARS}")

logger.debug(f"AI COMMAND: {AI_ENV.get("AI_PATH")} {AI_ENV.get("AI_ARGS")}")

def start_ai():
    log_path = get_log_path("ai")

    process = None
    try:
        with open(log_path, "w") as logfile:
            process = subprocess.Popen(
                [AI_ENV.get("AI_PATH")] + AI_ENV.get("AI_ARGS", "").split(' '),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  
            )
            for line in process.stdout:
                clean_line = strip_ansi(line)
                logfile.write(clean_line)
                logfile.flush()
            process.wait()
    except Exception as e:
        logger.error("Error during server monitoring:", e)
    finally:
        if process and process.poll() is None:
            process.terminate()
