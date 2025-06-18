##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## parsing
##

from .player import PlayerState

def parse_inventory(message: str, state: PlayerState):
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
        print(f"Inventory updated: {state.inventory}")
    except Exception as e:
        print(f"Could not parse inventory: {message} ({e})")

def parse_look(message: str, state: PlayerState):
    """
    Update the vision from the server's answer.
    """
    message = message.strip('[] \n')
    state.vision = [tile.strip() for tile in message.split(',')]
    print(f"Vision updated. Seeing {len(state.vision)} tiles.")
    print(f"On my tile (0): {state.vision[0] if state.vision else 'nothing'}")
