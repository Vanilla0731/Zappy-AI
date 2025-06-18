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

FOOD_SURVIVAL_THRESHOLD = 5 * 126 # 1 food = 126 time units, 20 food is the minimum to survive



class ZappyAI:
    def __init__(self, host: str, port: int, team_name: str):
        self.host = host
        self.port = port
        self.team_name = team_name
        self.sock = None
        self.buffer = ""

        # World and Player data
        self.world_width = 0
        self.world_height = 0
        self.inventory = {}
        self.level = 1
        self.is_alive = True

        self.vision = []

        # Command Queue
        self.command_queue = []

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
        last_command = self.command_queue.pop(0) if self.command_queue else ""
        if message == "ko":
            print(f"Command '{last_command}' failed.")
            return

        if message == "dead":
            self.is_alive = False
            print("--- I DIED ---")
            return

        if message.startswith("Current level:"):
            self.level = int(message.split(":")[1].strip())
            print(f"--- LEVEL UP! Now level {self.level} ---")
            # Reset the vision
            self.vision = []

        if last_command == "Inventory":
            self._parse_inventory(message)
        elif last_command == "Look":
            self._parse_look(message)
        elif last_command == "Connect_nbr":
            print(f"Available connection slots: {message}")
        elif last_command == "Fork":
            print("Successfully laid an egg!")


    def _parse_inventory(self, message: str):
        """
        Update the inventory from the server's answer.
        """
        message = message.strip('[] \n')
        if not message:
            return
        try:
            items = message.split(',')
            for item in items:
                name, quantity = item.strip().split()
                self.inventory[name] = int(quantity)
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
                    self.send_command("Inventory")
                    self._make_decision()

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
        # Priority 1: SURVIVAL
        if self.inventory.get("food", 0) * 126 < FOOD_SURVIVAL_THRESHOLD:
            print("Decision: Low on food, must find some to survive.")
            # If there is food on the current tile, take it.
            if self.vision and "food" in self.vision[0]:
                self.send_command("Take food")
            else:
                # If no food is visible, move randomly to find some.
                self.send_command(random.choice(["Forward", "Left", "Right"]))
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
            print("Decision: I have all stones for the next level. Preparing for incantation.")
            # Setting stones on the tile
            requirements = ELEVATION_REQUIREMENTS[self.level][1]
            for stone, count in requirements.items():
                if count > 0:
                    for _ in range(count):
                        self.send_command(f"Set {stone}")
            #Starting the Incantation
            self.send_command("Incantation")
            return

        # Priority 4: GATHERING
        if self.vision:
            tile_content = self.vision[0].split()
            for stone in needed_for_elevation:
                if stone in tile_content:
                    print(f"Decision: Found a needed stone ({stone}) on my tile. Taking it.")
                    self.send_command(f"Take {stone}")
                    return

        # Priority 5: EXPLORATION
        print("Decision: Exploring the world to find resources.")
        if not self.vision:
            self.send_command("Look")  # "Look" before moving
        else:
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
