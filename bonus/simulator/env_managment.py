##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## env_managment
##

from os import path
from .exception import SimError, try_sim
from dotenv import load_dotenv as _load_dotenv

DOTENV_PATHS = [
    ".",
    path.dirname(path.dirname(path.abspath(__file__)))
]

@try_sim
def load_dotenv() -> None:
    dotenv_path = None

    for filepath in DOTENV_PATHS:
        tmppath = path.realpath(path.join(filepath, ".env"))
        if path.exists(tmppath):
            dotenv_path = tmppath
            break

    if dotenv_path is None:
        raise SimError("load_dotenv", "could not find .env")

    _load_dotenv(dotenv_path, override=True)
