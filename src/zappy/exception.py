##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## exception
##

class ZappyError(Exception):
    def __init__(self, where: str, what: str) -> None:
        self.where = where
        self.what = what
        super().__init__(f"An error happened at {where}: {what}")
