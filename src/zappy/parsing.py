##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## parsing
##

from . import logger
from .player import PlayerState

def parse_inventory(message: str, state: PlayerState) -> None:
    """
    Update the inventory from the server's answer.
    """
    message = message.strip('[] \n')
    new_inventory = {}
    if not message:
        state.inventory = new_inventory # Empty inventory case
        return
    try:
        items = message.split(',')
        for item in items:
            name, quantity = item.strip().split()
            new_inventory[name] = int(quantity)
        # Assign the new inventory
        state.inventory = new_inventory
        logger.debug(f"Inventory updated: {state.inventory}")
    except ValueError:
        logger.warning(f"Could not parse inventory: {message}")

def parse_look(message: str, state: PlayerState) -> None:
    """
    Update the vision from the server's answer.
    """
    message = message.strip('[] \n')
    state.vision = [tile.strip() for tile in message.split(',')]
    logger.debug(f"Vision updated. Seeing {len(state.vision)} tiles.")
    logger.debug(f"On my tile (0): {state.vision[0] if state.vision else 'nothing'}")
