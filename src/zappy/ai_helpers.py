##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## parser
##

from . import ELEVATION_REQUIREMENTS

def find_closest_ressource(vision: list[str], ressource_name: str) -> int:
    """
    Find the closest tile in vision containing the specifies ressource.
    Returns the tile index, or -1 if not found.
    """
    if not vision:
        return -1
    for i, tile_content in enumerate(vision):
        if ressource_name in tile_content:
            return i
    return -1

def get_path_to_tile(tile_index: int):
    """
    Find the path to a tile and generate the sequence of commands to move to it.
    """
    if tile_index <= 0:
        return []

    path = []
    level = 0
    tiles_in_level = 1
    # Calculate the depth of the tile
    while tile_index >= tiles_in_level:
        tile_index -= tiles_in_level
        level += 1
        tiles_in_level = 2 * level + 1
    # Now tile_index is the index in the current level

    # 1. Move to the correct level
    path.extend(["Forward"] * level)

    # 2. Move to the correct tile in the level
    center_of_level = level
    if tile_index < center_of_level:
        path.append("Left")
        # Move to the left side of the level
        path.extend(["Forward"] * (center_of_level - tile_index))
    elif tile_index > center_of_level:
        path.append("Right")
        # Move to the right side of the level
        path.extend(["Forward"] * (tile_index - center_of_level))
    else:
        # Already at the center of the level
        pass
    return path

def check_elevation_requirements(level: int, inventory: dict[str, int]):
    """
    Check if the needed stones are available for the ritual.
    Return the missing ones or a message if already at max level.
    """
    if level >= 8:
        return {"status": "max_level"}

    requirements = ELEVATION_REQUIREMENTS[level][1]
    missing = {}
    for stone, required_count in requirements.items():
        if inventory.get(stone, 0) < required_count:
            missing[stone] = required_count - inventory.get(stone, 0)
    return missing

def get_path_from_direction(direction: int):
    """
    Generate a sequence of commands to move towards the source of a sound.
    The direction indicates the tile from which the sound is coming.
    """
    if direction == 0: # Sound is coming from the current tile
        return []

    # Mapping of directions to movement commands
    # 1: Forward, 3: Left, 5: Behind, 7: Right
    paths = {
        1: ["Forward"],
        2: ["Forward", "Left", "Forward"],
        3: ["Left", "Forward"],
        4: ["Left", "Forward", "Left", "Forward"],
        5: ["Left", "Left", "Forward"],
        6: ["Right", "Forward", "Right", "Forward"],
        7: ["Right", "Forward"],
        8: ["Forward", "Right", "Forward"],
    }
    return paths.get(direction, [])
