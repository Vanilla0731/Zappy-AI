##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## decision_engine
##

import random
from . import logger
from .server import ZappyServer
from .player import PlayerState
from . import ELEVATION_REQUIREMENTS, FOOD_SURVIVAL_THRESHOLD

FORK_TIMER = 40

class DecisionEngine(ZappyServer, PlayerState):
    def __init__(self, host: str, port: int, team_name: str) -> None:
        ZappyServer.__init__(self, host, port)
        PlayerState.__init__(self, team_name)
        self.timer_fork = FORK_TIMER

    @staticmethod
    def _get_path_to_tile(tile_index: int) -> list:
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

    @staticmethod
    def _find_closest_ressource(vision: list[str], ressource_name: str) -> int:
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

    @staticmethod
    def _check_elevation_requirements(level: int, inventory: dict[str, int]) -> (dict[str, str] | dict):
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

    def _respond_to_broadcast(self) -> bool:
        if self.is_responding_to_broadcast and not self.action_plan:
            self.is_responding_to_broadcast = False
            self.send_command("Look")
            return True
        return False

    def _update_vision(self) -> bool:
        if not self.vision:
            self.send_command("Look")
            return True
        return False

    def _survive(self) -> bool:
        if self.inventory.get("food", 0) * 126 < FOOD_SURVIVAL_THRESHOLD:
            logger.debug("Decision: Low on food, must find some to survive.")
            self.is_responding_to_broadcast = False
            food_tile_index = self._find_closest_ressource(self.vision, "food")

            # If there is food on the current tile, take it.
            if food_tile_index == 0:
                self.send_command("Take food")
            elif food_tile_index > 0:
                # If food is visible on another tile, move towards it.
                logger.debug(f"Decision: Found food on tile {food_tile_index}. Moving towards it.")
                self.action_plan = self._get_path_to_tile(food_tile_index)
                self.action_plan.append("Take food")
            else:
                # If no food is visible, move randomly to find some.
                self.send_command(random.choice(["Forward", "Left", "Right"]))
            self.vision = []  # Vision would be invalid after moving
            return True
        return False

    def _reproduct(self) -> bool:
        # Fork when we have enough food and are at a decent level
        logger.debug(f"check value : {self.inventory.get('food', 0) * 126}")
        logger.debug(f'Food attendue : {FOOD_SURVIVAL_THRESHOLD}')
        if (self.inventory.get("food", 0) * 126 >= FOOD_SURVIVAL_THRESHOLD and
            self.level >= 2 and
            self.timer_fork == 0):
            logger.debug("Decision: Conditions are good for reproduction. Forking...")
            self.send_command("Fork")
            self.timer_fork = FORK_TIMER
            return True
        return False

    def _elevate(self) -> bool:
        needed_for_elevation = self._check_elevation_requirements(self.level, self.inventory)
        if not needed_for_elevation:
            if self.inventory.get("food", 0) * 126 < 300 + (2 * 126): # 300 time units for incantation + 2 * 126 for the next level
                logger.debug("Decision: Ready for elevation, but need food first to survive the ritual.")
                self.send_command("Look")
                return True

            players_needed = ELEVATION_REQUIREMENTS[self.level][0]
            players_on_tile = self.vision[0].count("player")

            if players_on_tile >= players_needed:
                logger.debug("Decision: I have all stones and enough players for the next level. Preparing for incantation.")
                self.is_responding_to_broadcast = False
                # Setting stones on the tile
                requirements = ELEVATION_REQUIREMENTS[self.level][1]
                for stone, count in requirements.items():
                    if count > 0:
                        for _ in range(count):
                            self.action_plan.append(f"Set {stone}")
                #Starting the Incantation
                self.action_plan.append("Incantation")
            else:
                logger.debug(f"Decision: Waiting for {players_needed - players_on_tile} more players to start incantation.")
                message = f"{self.team_name}:Incantation:{self.level}"
                self.send_command(f"Broadcast {message}")
                # Looking around while waiting for more players
                self.send_command("Look")
            return True
        return False

    def _gather(self) -> bool:
        needed_for_elevation = self._check_elevation_requirements(self.level, self.inventory)
        closest_stone = {"stone": None, "tile_index": -1}
        for stone in needed_for_elevation:
            tile_index = self._find_closest_ressource(self.vision, stone)
            if tile_index != -1:
                # First stone found or closest one
                if closest_stone["tile_index"] == -1 or tile_index < closest_stone["tile_index"]:
                    closest_stone["stone"] = stone
                    closest_stone["tile_index"] = tile_index

        if closest_stone["stone"]:
            stone_to_get = closest_stone["stone"]
            tile_to_go = closest_stone["tile_index"]
            logger.debug(f"Decision: Found {stone_to_get} on tile {tile_to_go}. Moving towards it.")
            if tile_to_go == 0:
                self.send_command(f"Take {stone_to_get}")
            else:
                self.action_plan = self._get_path_to_tile(tile_to_go)
                self.action_plan.append(f"Take {stone_to_get}")

            self.vision = []  # Vision would be invalid after moving
            return True
        return False

    def _explore(self) -> bool:
        logger.debug("Decision: Exploring the world to find resources.")
        self.send_command("Forward")
        # A bit of random to not go only forward
        if random.randint(0, 5) == 0:
            self.send_command(random.choice(["Left", "Right"]))
        self.vision = []
        return True

    def make_decision(self):
        """
        Make decisions based on the current state of the AI.
        This method should be implemented with the AI's logic.
        """
        actions = [self._respond_to_broadcast,
                   self._update_vision,
                   self._survive,
                   self._reproduct,
                   self._elevate,
                   self._gather,
                   self._explore]

        any(action() for action in actions)
