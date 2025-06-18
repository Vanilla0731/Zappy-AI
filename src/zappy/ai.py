##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## AI
##

import sys
import random
from .server import ZappyServer
from . import ELEVATION_REQUIREMENTS, FOOD_SURVIVAL_THRESHOLD
from .ai_helpers import (find_closest_ressource, get_path_to_tile,
    check_elevation_requirements, get_path_from_direction)

class ZappyAI:
    def __init__(self, host: str, port: int, team_name: str):
        self.sock = ZappyServer(host, port)

        # World and Player data
        self.level = 1
        self.vision = []
        self.inventory = {}
        self.world_width = 0
        self.is_alive = True
        self.world_height = 0
        self.action_plan = []
        self.team_name = team_name
        self.is_responding_to_broadcast = False

    def _initial_connection(self):
        """
        Waits for 'WELCOME' and sends the team name.
        """
        welcome_message = self.sock.read_from_server()
        if welcome_message != "WELCOME":
            print(f"Error: Expected 'WELCOME' from server, but got '{welcome_message}'", file=sys.stderr)
            sys.exit(84)

        print(f"Server -> Me: {welcome_message}")
        print(f"Me -> Server: {self.team_name}")
        self.sock.send_command_immediately(f"{self.team_name}")
        client_num_str = self.sock.read_from_server()
        if client_num_str == "ko":
            print("Error: Team can't have more members.", file=sys.stderr)
            sys.exit(84)

        world_size_str = self.sock.read_from_server()
        print(f"Server -> Me: {world_size_str}")
        self.world_width, self.world_height = map(int, world_size_str.split())
        print(f"World size: {self.world_width}x{self.world_height}")

    def handle_server_message(self, message: str):
        """
        Handle messages received from the server.
        This method may be extended to handle different types of messages.
        """
        # Holding of every non-solicited messages

        if message.startswith("message"):
            self._handle_broadcast(message)
            return

        # "Elevation underway" is a notification, we must ignore it
        if message == "Elevation underway":
            print(f"INFO: An elevation ritual is underway on the tile.")
            return

        # "Current level: n" is the result of an incantation.
        if message.startswith("Current level:"):
            self.sock.pop_incantation()

            self.level = int(message.split(":")[1].strip())
            print(f"--- LEVEL UP! Now level {self.level} ---")
            self.vision = [] # Reset the vision
            self.is_responding_to_broadcast = False
            self.action_plan = []  # Clear the action plan
            return

        # Fatal notification
        if message == "dead":
            self.is_alive = False
            print("--- I DIED ---")
            return

        # Handling of answers to commands
        if not self.sock.get_command_queue():
            print(f"Warning: Received message '{message}' without any command in the queue. Ignoring.")
            return

        last_command = self.sock.pop_last_command()

        # If the command failed, cancel the action plan
        if message == "ko":
            print(f"Command '{last_command}' failed.")
            self.action_plan = []
            return

        # If the command was successful, no need for a specific treatment
        if message == "ok":
            return

        # If the command was "Inventory" or "Look", we parse the message
        match last_command:
            case "Inventory":
                self._parse_inventory(message)
            case"Look":
                self._parse_look(message)
            case "Connect_nbr":
                print(f"Available connection slots: {message}")
            case "Fork":
                print("Successfully laid an egg!")
            case _: # Weird case where we receive an unexpected answer for a known command. This should not happen.
                print(f"WARNING: Received unexpected answer '{message}' for command '{last_command}'.")

    def _parse_inventory(self, message: str):
        """
        Update the inventory from the server's answer.
        """
        message = message.strip('[] \n')
        new_inventory = {}
        if not message:
            self.inventory = new_inventory # Empty inventory case
            return
        try:
            items = message.split(',')
            for item in items:
                name, quantity = item.strip().split()
                new_inventory[name] = int(quantity)
            # Assign the new inventory
            self.inventory = new_inventory
            print(f"Inventory updated: {self.inventory}")
        except Exception as e:
            print(f"Could not parse inventory: {message} ({e})")

    def _parse_look(self, message: str):
        """
        Update the vision from the server's answer.
        """
        message = message.strip('[] \n')
        self.vision = [tile.strip() for tile in message.split(',')]
        print(f"Vision updated. Seeing {len(self.vision)} tiles.")
        print(f"On my tile (0): {self.vision[0] if self.vision else 'nothing'}")

    def _handle_broadcast(self, message: str):
        """
        Parses and reacts to a broadcast message from another player.
        Exemple de message du serveur: "message 2, NOM_EQUIPE:incantation:4"
        """
        print(f"Broadcast received: {message}")
        try:
            # Format: "message K, text"
            direction_str, content = message.replace("message ", "").split(",", 1)
            direction = int(direction_str)
            content = content.strip()
        except ValueError:
            print(f"Could not parse broadcast: {message}")
            return

        # 1. Ignore the message if it comes from ourselves or if it is coming from the current tile (direction 0)
        if direction == 0 or self.is_responding_to_broadcast:
            return

        # 2. Parse the content of the message
        # Format: TEAM_NAME:purpose:level
        try:
            team_name, purpose, level_str = content.split(":")
            required_level = int(level_str)
        except (ValueError, IndexError):
            # Ignore messages with invalid format
            return

        # 3. Check if the message is relevant to us
        if team_name == self.team_name and purpose == "Incantation" and self.level == required_level:
            print(f"Decision: Responding to incantation call for level {required_level} from direction {direction}.")
            self.is_responding_to_broadcast = True
            self.action_plan = get_path_from_direction(direction)
            # Look around to see if we can help
            self.action_plan.append("Look")

    def run(self):
        """
        Main loop for the AI client.
        """
        self.sock.connect_to_server()
        self._initial_connection()
        self.sock.send_command("Inventory")

        while self.is_alive:
            try:
                if not self.sock.get_command_queue():
                    if not self.action_plan:
                        self.sock.send_command("Inventory")
                        self._make_decision()

                while self.action_plan and len(self.sock.get_command_queue()) < 10:
                    next_action = self.action_plan.pop(0)
                    self.sock.send_command(next_action)

                # Waiting for server answers
                message = self.sock.read_from_server()
                print(f"Server -> Me: {message}")
                self.handle_server_message(message)

            except KeyboardInterrupt:
                print("\rUser interruption. Closing connection.")
                break
            except Exception as e:
                print(f"An error occurred in the main loop: {e}", file=sys.stderr)
                break

        if self.sock:
            self.sock.close()
            print("Socket closed.")

    def _respond_to_broadcast(self):
        if self.is_responding_to_broadcast and not self.action_plan:
            self.is_responding_to_broadcast = False
            self.sock.send_command("Look")
            return True
        return False

    def _update_vision(self):
        if not self.vision:
            self.sock.send_command("Look")
            return True
        return False

    def _survive(self):
        if self.inventory.get("food", 0) * 126 < FOOD_SURVIVAL_THRESHOLD:
            print("Decision: Low on food, must find some to survive.")
            self.is_responding_to_broadcast = False
            food_tile_index = find_closest_ressource(self.vision, "food")

            # If there is food on the current tile, take it.
            if food_tile_index == 0:
                self.sock.send_command("Take food")
            elif food_tile_index > 0:
                # If food is visible on another tile, move towards it.
                print(f"Decision: Found food on tile {food_tile_index}. Moving towards it.")
                self.action_plan = get_path_to_tile(food_tile_index)
                self.action_plan.append("Take food")
            else:
                # If no food is visible, move randomly to find some.
                self.sock.send_command(random.choice(["Forward", "Left", "Right"]))
            self.vision = []  # Vision would be invalid after moving
            return True
        return False

    def _reproduct(self):
        # Fork when we have enough food and are at a decent level
        if (self.inventory.get("food", 0) * 126 > FOOD_SURVIVAL_THRESHOLD * 2 and
            self.level >= 2 and
            random.randint(0, 20) == 0):
            print("Decision: Conditions are good for reproduction. Forking...")
            self.send_command("Fork")
            return True
        return False

    def _elevate(self):
        needed_for_elevation = check_elevation_requirements(self.level, self.inventory)
        if not needed_for_elevation:
            if self.inventory.get("food", 0) * 126 < 300 + (2 * 126): # 300 time units for incantation + 2 * 126 for the next level
                print("Decision: Ready for elevation, but need food first to survive the ritual.")
                self.send_command("Look")
                return

            players_needed = ELEVATION_REQUIREMENTS[self.level][0]
            players_on_tile = self.vision[0].count("player") + 1 # +1 for self

            if players_on_tile >= players_needed:
                print("Decision: I have all stones and enough players for the next level. Preparing for incantation.")
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
                print(f"Decision: Waiting for {players_needed - players_on_tile} more players to start incantation.")
                message = f"{self.team_name}:Incantation:{self.level}"
                self.send_command(f"Broadcast {message}")
                # Looking around while waiting for more players
                self.send_command("Look")
            return True
        return False

    def _gather(self):
        needed_for_elevation = check_elevation_requirements(self.level, self.inventory)
        closest_stone = {"stone": None, "tile_index": -1}
        for stone in needed_for_elevation:
            tile_index = find_closest_ressource(self.vision, stone)
            if tile_index != -1:
                # First stone found or closest one
                if closest_stone["tile_index"] == -1 or tile_index < closest_stone["tile_index"]:
                    closest_stone["stone"] = stone
                    closest_stone["tile_index"] = tile_index

        if closest_stone["stone"]:
            stone_to_get = closest_stone["stone"]
            tile_to_go = closest_stone["tile_index"]
            print(f"Decision: Found {stone_to_get} on tile {tile_to_go}. Moving towards it.")
            if tile_to_go == 0:
                self.send_command(f"Take {stone_to_get}")
            else:
                self.action_plan = get_path_to_tile(tile_to_go)
                self.action_plan.append(f"Take {stone_to_get}")

            self.vision = []  # Vision would be invalid after moving
            return True
        return False

    def _explore(self):
        print("Decision: Exploring the world to find resources.")
        self.send_command("Forward")
        # A bit of random to not go only forward
        if random.randint(0, 5) == 0:
            self.send_command(random.choice(["Left", "Right"]))
        self.vision = []
        return True

    def _make_decision(self):
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
