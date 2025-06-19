##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## player
##

class PlayerState:
    def __init__(self, team_name: str) -> None:
        self.level = 1
        self.timer_fork = 40
        self.vision = []
        self.inventory = {}
        self.is_alive = True
        self.world_width = 0
        self.world_height = 0
        self.action_plan = []
        self.team_name = team_name
        self.is_responding_to_broadcast = False

    def reset_vision(self) -> None:
        self.vision = []

    def reset_action_plan(self) -> None:
        self.action_plan = []

    def update_inventory(self, inventory: dict) -> None:
        self.inventory = inventory

    def update_vision(self, vision: list) -> None:
        self.vision = vision

    def set_world_size(self, width: int, height: int) -> None:
        self.world_width = width
        self.world_height = height

    def die(self) -> None:
        self.is_alive = False

    def level_up(self) -> None:
        self.level += 1
        self.reset_vision()
        self.is_responding_to_broadcast = False
        self.reset_action_plan()

    def get_team_name(self) -> str:
        return self.team_name

    def get_level(self) -> int:
        return self.level

    def get_world_width(self) -> int:
        return self.world_width

    def get_world_height(self) -> int:
        return self.world_height
