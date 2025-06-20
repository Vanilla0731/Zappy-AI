##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## exception
##

from . import logger, SIM_ERROR

class SimError(Exception):
    def __init__(self, where: str, what: str) -> None:
        self.where = where
        self.what = what
        super().__init__(f"An error happened at {where}: {what}")

def try_sim(func):
    def wrapper():
        try:
            return func()
        except SimError as e:
            logger.error(f"An error occured at {e.where}: {e.what}")
            exit(SIM_ERROR)
    return wrapper
