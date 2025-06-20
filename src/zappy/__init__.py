##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## __init__
##

# logger initialization
from .logger import init_logger

logger = init_logger()

# Constants for the AI client
ELEVATION_REQUIREMENTS = {
    1: (1, {"linemate": 1, "deraumere": 0, "sibur": 0, "mendiane": 0, "phiras": 0, "thystame": 0}),
    2: (2, {"linemate": 1, "deraumere": 1, "sibur": 1, "mendiane": 0, "phiras": 0, "thystame": 0}),
    3: (2, {"linemate": 2, "deraumere": 0, "sibur": 1, "mendiane": 0, "phiras": 2, "thystame": 0}),
    4: (4, {"linemate": 1, "deraumere": 1, "sibur": 2, "mendiane": 0, "phiras": 1, "thystame": 0}),
    5: (4, {"linemate": 1, "deraumere": 2, "sibur": 1, "mendiane": 3, "phiras": 0, "thystame": 0}),
    6: (6, {"linemate": 1, "deraumere": 2, "sibur": 3, "mendiane": 0, "phiras": 1, "thystame": 0}),
    7: (6, {"linemate": 2, "deraumere": 2, "sibur": 2, "mendiane": 2, "phiras": 2, "thystame": 1}),
}

ACTION_SPEED = [
    ["inventory"],
    ["forward", "right", "left", "look", "broadcast", "eject", "take", "set"],
    ["fork"],
    ["incantation"]
]

FOOD_SURVIVAL_THRESHOLD = 8 * 126 # 1 food = 126 time units, 20 food is the minimum to survive

RESOURCES = [
    "food", "linemate", "deraumere", "sibur", "mendiane", "phiras", "thystame"
]

ACTIONS = [
    "Forward", "Right", "Left", "Look", "Inventory", "Incantation", "Fork"
]

for resource in RESOURCES:
    ACTIONS.append(f"Take {resource.capitalize()}")
    ACTIONS.append(f"Set {resource.capitalize()}")

# Exemple: ACTIONS[0] -> "Forward" ; ACTIONS[7] -> "Take food"