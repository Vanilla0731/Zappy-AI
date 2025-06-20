##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## monitor_thread
##

import threading
from . import logger


def monitor_thread(thread, target_function):
    while True:
        if not thread.is_alive():
            logger.info(f"Thread {thread.name} terminated. Restarting...")
            thread = threading.Thread(target=target_function, name=thread.name)
            thread.start()
        thread.join(1)
