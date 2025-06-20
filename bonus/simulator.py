##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## simulator
##

import signal
import threading
from os import _exit, getenv
from simulator.env_managment import load_dotenv
from simulator.exception import SimError, try_sim
from simulator.monitor_thread import monitor_thread
from simulator import logger, SIM_ERROR, SIM_SUCCESS

load_dotenv()

try:
    MAIN_ENV = {
        "NUM_AI": int(getenv("NUM_AI"))
    }

    UNINITIALIZED_VARS = [k for k, v in MAIN_ENV.items() if v is None]

    if UNINITIALIZED_VARS:
        raise SimError("start_server", f"The following environment variables should be initialized but they are not: {UNINITIALIZED_VARS}")

    if MAIN_ENV.get("NUM_AI") < 0:
        raise ValueError

    from simulator.start_server import start_server
    from simulator.start_ai import start_ai
except (TypeError, ValueError):
    logger.error(f"An error occured at main: NUM_AI is not a positive int")
    exit(SIM_ERROR)
except SimError as e:
    logger.error(f"An error occured at {e.where}: {e.what}")
    exit(SIM_ERROR)

def signal_handler(sig, frame):
    sig_str = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
    logger.info(f"\r{sig_str} detected. Stopping simulator.")
    _exit(SIM_SUCCESS)

def start_threads() -> tuple[threading.Thread, list[threading.Thread]]:
    server_thread = threading.Thread(target=start_server, name="server_thread")

    NUM_AI = MAIN_ENV.get("NUM_AI")
    logger.debug(f"USING NUM_AI={NUM_AI}")

    ai_threads: list[threading.Thread] = []
    for i in range(NUM_AI):
        ai_threads.append(threading.Thread(target=start_ai, name=f"ai_{i}_thread"))

    server_thread.start()
    for thread in ai_threads:
        thread.start()

    return server_thread, ai_threads

def start_monitors(server_thread: threading.Thread, ai_threads: list[threading.Thread]) -> None:
    server_monitor = threading.Thread(target=monitor_thread,
                                      args=(server_thread, start_server))

    ai_monitors: list[threading.Thread] = []
    for thread in ai_threads:
        ai_monitors.append(threading.Thread(target=monitor_thread,
                                            args=(thread, start_ai)))
    server_monitor.start()
    for thread in ai_monitors:
        thread.start()

    server_monitor.join()
    for thread in ai_monitors:
        thread.join()

@try_sim
def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server_thread, ai_threads = start_threads()
    start_monitors(server_thread, ai_threads)

if __name__ == "__main__":
    main()
    exit(SIM_SUCCESS)
