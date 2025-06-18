##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## player
##

from typing import Any

class PlayerState:
    def __init__(self, team_name: str, **kwargs: dict[str, Any]):
        self.level = 1
        self.vision = []
        self.inventory = {}
        self.is_alive = True
        self.world_width = 0
        self.world_height = 0
        self.action_plan = []
        self.team_name = team_name
        self.is_responding_to_broadcast = False

    def reset_vision(self):
        self.vision = []

    def reset_action_plan(self):
        self.action_plan = []

    def update_inventory(self, inventory: dict):
        self.inventory = inventory

    def update_vision(self, vision: list):
        self.vision = vision

    def set_world_size(self, width: int, height: int):
        self.world_width = width
        self.world_height = height

    def die(self):
        self.is_alive = False

    def level_up(self):
        self.level += 1
        self.reset_vision()
        self.is_responding_to_broadcast = False
        self.reset_action_plan()

    def get_team_name(self):
        return self.team_name

    def get_level(self):
        return self.level

    def get_world_width(self):
        return self.world_width

    def get_world_height(self):
        return self.world_height
