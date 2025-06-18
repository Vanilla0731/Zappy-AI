##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## main
##

import sys
import argparse
import socket
import random

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

FOOD_SURVIVAL_THRESHOLD = 8 * 126 # 1 food = 126 time units, 20 food is the minimum to survive


class ZappyAI:
    def __init__(self, host: str, port: int, team_name: str):
        self.host = host
        self.port = port
        self.team_name = team_name
        self.sock = None
        self.buffer = ""
        self.is_responding_to_broadcast = False

        # World and Player data
        self.world_width = 0
        self.world_height = 0
        self.inventory = {}
        self.level = 1
        self.is_alive = True
        self.vision = []

        # Command Queue
        self.command_queue = []
        self.action_plan = []

    def connect_to_server(self):
        """
        Create the socket(s) and connect to the Zappy server.
        """
        print(f"Trying to connect to Zappy server at {self.host}:{self.port}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print("Connection established with Zappy server.")

        except ConnectionRefusedError:
            print(f"Error: Connection denied.", file=sys.stderr)
            sys.exit(1)
        except socket.timeout:
            print("Error: No response from the server (timeout).", file=sys.stderr)
            sys.exit(1)


    def _read_from_server(self):
        """
        Reads from the server buffer until a newline character is found.
        """
        while "\n" not in self.buffer:
            if self.sock is None:
                print("Error: Socket is not connected.", file=sys.stderr)
                sys.exit(1)
            data = self.sock.recv(1024).decode('utf-8')
            if not data:
                print("Connection closed by the server.")
                sys.exit(0)
            self.buffer += data

        line, self.buffer = self.buffer.split("\n", 1)
        return line


    def _initial_connection(self):
        """
        Waits for 'WELCOME' and sends the team name.
        """
        welcome_message = self._read_from_server()
        if welcome_message != "WELCOME":
            print(f"Error: Expected 'WELCOME' from server, but got '{welcome_message}'", file=sys.stderr)
            sys.exit(84)

        print(f"Server -> Me: {welcome_message}")
        print(f"Me -> Server: {self.team_name}")
        self.send_command_immediately(f"{self.team_name}")
        client_num_str = self._read_from_server()
        if client_num_str == "ko":
            print("Error: Team can't have more members.", file=sys.stderr)
            sys.exit(84)

        world_size_str = self._read_from_server()
        print(f"Server -> Me: {world_size_str}")
        self.world_width, self.world_height = map(int, world_size_str.split())
        print(f"World size: {self.world_width}x{self.world_height}")


    def send_command_immediately(self, command: str):
        """
        Send a command without using the command queue (for initial connection).
        """
        if self.sock is not None:
            self.sock.sendall(f"{command}\n".encode('utf-8'))
        else:
            print("Error: Socket is not connected.", file=sys.stderr)
            sys.exit(1)


    def send_command(self, command: str):
        """
        Add a command to the command queue and send it to the server.
        """
        if len(self.command_queue) < 10:
            print(f"Me -> Server: {command}")
            self.send_command_immediately(command)
            self.command_queue.append(command)
            return True
        else:
            print("Warning: Command queue is full. Cannot send new command yet.")
        return False


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
            try:
                incantation_index = self.command_queue.index("Incantation")
                del self.command_queue[:incantation_index + 1]  # Remove the incantation command and its dependencies
            except ValueError:
                pass  # In case "Incantation" is not in the queue, we ignore it

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

        if not self.command_queue:
            print(f"Warning: Received message '{message}' without any command in the queue. Ignoring.")
            return

        last_command = self.command_queue.pop(0)

        # If the command failed, cancel the action plan
        if message == "ko":
            print(f"Command '{last_command}' failed.")
            self.action_plan = []
            return

        # If the command was successful, no need for a specific treatment
        if message == "ok":
            return

        # If the command was "Inventory" or "Look", we parse the message
        if last_command == "Inventory":
            self._parse_inventory(message)
        elif last_command == "Look":
            self._parse_look(message)
        elif last_command == "Connect_nbr":
            print(f"Available connection slots: {message}")
        elif last_command == "Fork":
            print("Successfully laid an egg!")
        else: # Weird case where we receive an unexpected answer for a known command. This should not happen.
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


    def _check_elevation_requirements(self):
        """
        Check if the needed stones are available for the ritual.
        Return the missing ones or a message if already at max level.
        """
        if self.level >= 8:
            return {"status": "max_level"}

        requirements = ELEVATION_REQUIREMENTS[self.level][1]
        missing = {}
        for stone, required_count in requirements.items():
            if self.inventory.get(stone, 0) < required_count:
                missing[stone] = required_count - self.inventory.get(stone, 0)
        return missing


    def _find_closest_ressource(self, ressource_name: str) -> int:
        """
        Find the closest tile in vision containing the specifies ressource.
        Returns the tile index, or -1 if not found.
        """
        if not self.vision:
            return -1
        for i, tile_content in enumerate(self.vision):
            if ressource_name in tile_content:
                return i
        return -1


    def _get_path_to_tile(self, tile_index: int):
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


    def _get_path_from_direction(self, direction: int):
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
            self.action_plan = self._get_path_from_direction(direction)
            # Look around to see if we can help
            self.action_plan.append("Look")


    def run(self):
        """
        Main loop for the AI client.
        """
        self.connect_to_server()
        self._initial_connection()
        self.send_command("Inventory")

        while self.is_alive:
            try:
                if not self.command_queue:
                    if not self.action_plan:
                        self.send_command("Inventory")
                        self._make_decision()

                while self.action_plan and len(self.command_queue) < 10:
                    next_action = self.action_plan.pop(0)
                    self.send_command(next_action)

                # Waiting for server answers
                message = self._read_from_server()
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


    def _make_decision(self):
        """
        Make decisions based on the current state of the AI.
        This method should be implemented with the AI's logic.
        """
        # If answering to a broadcast, we only follow the broadcast
        if self.is_responding_to_broadcast and not self.action_plan:
            self.is_responding_to_broadcast = False
            self.send_command("Look")
            return

        # Priority 0: Update vision
        if not self.vision:
            self.send_command("Look")
            return

        # Priority 1: SURVIVAL
        if self.inventory.get("food", 0) * 126 < FOOD_SURVIVAL_THRESHOLD:
            print("Decision: Low on food, must find some to survive.")
            self.is_responding_to_broadcast = False
            food_tile_index = self._find_closest_ressource("food")

            # If there is food on the current tile, take it.
            if food_tile_index == 0:
                self.send_command("Take food")
            elif food_tile_index > 0:
                # If food is visible on another tile, move towards it.
                print(f"Decision: Found food on tile {food_tile_index}. Moving towards it.")
                self.action_plan = self._get_path_to_tile(food_tile_index)
                self.action_plan.append("Take food")
            else:
                # If no food is visible, move randomly to find some.
                self.send_command(random.choice(["Forward", "Left", "Right"]))
            self.vision = []  # Vision would be invalid after moving
            return

        # Priority 2: REPRODUCTION (Fork)
        # Fork when we have enough food and are at a decent level
        if (self.inventory.get("food", 0) * 126 > FOOD_SURVIVAL_THRESHOLD * 2 and
            self.level >= 2 and
            random.randint(0, 20) == 0):
            print("Decision: Conditions are good for reproduction. Forking...")
            self.send_command("Fork")
            return

        # Priority 3: ELEVATION
        needed_for_elevation = self._check_elevation_requirements()
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
            return

        # Priority 4: GATHERING
        closest_stone = {"stone": None, "tile_index": -1}
        for stone in needed_for_elevation:
            tile_index = self._find_closest_ressource(stone)
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
                self.action_plan = self._get_path_to_tile(tile_to_go)
                self.action_plan.append(f"Take {stone_to_get}")

            self.vision = []  # Vision would be invalid after moving
            return

        # Priority 5: EXPLORATION
        print("Decision: Exploring the world to find resources.")
        self.send_command("Forward")
        # A bit of random to not go only forward
        if random.randint(0, 5) == 0:
            self.send_command(random.choice(["Left", "Right"]))
        self.vision = []


def main():
    """
    Entry point of the Zappy AI client.
    """
    parser = argparse.ArgumentParser(description="Zappy AI Client", add_help=False)
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to connect to the Zappy server')
    parser.add_argument('-n', '--name', type=str, required=True, help='Name of the team to join')
    parser.add_argument('-h', '--host', type=str, default='localhost', help='Host to connect to the Zappy server')

    args = parser.parse_args()

    try:
        ai_client = ZappyAI(host=args.host, port=args.port, team_name=args.name)
        ai_client.run()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"A critical error occurred: {e}", file=sys.stderr)
        sys.exit(84)

if __name__ == "__main__":
    main()
