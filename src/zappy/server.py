##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## server
##

import sys
import socket
from typing import Any
from .player import PlayerState
from .parsing import parse_inventory, parse_look

class ZappyServer:
    def __init__(self, host: str, port: int, **kwargs: dict[str, Any]):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = ""
        self.command_queue = []

    @staticmethod
    def _get_path_from_direction(direction: int):
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

    def initial_connection(self, state: PlayerState):
        """
        Waits for 'WELCOME' and sends the team name.
        """
        welcome_message = self.read_from_server()
        if welcome_message != "WELCOME":
            print(f"Error: Expected 'WELCOME' from server, but got '{welcome_message}'", file=sys.stderr)
            sys.exit(84)

        print(f"Server -> Me: {welcome_message}")
        print(f"Me -> Server: {state.get_team_name()}")
        self.send_command_immediately(f"{state.get_team_name()}")
        client_num_str = self.read_from_server()
        if client_num_str == "ko":
            print("Error: Team can't have more members.", file=sys.stderr)
            sys.exit(84)

        world_size_str = self.read_from_server()
        print(f"Server -> Me: {world_size_str}")
        width, heigth = map(int, world_size_str.split())
        state.set_world_size(width, heigth)
        print(f"World size: {state.get_world_height()}x{state.get_world_height()}")

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

    def read_from_server(self):
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

    def _handle_broadcast(self, message: str, state: PlayerState):
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
        if direction == 0 or state.is_responding_to_broadcast:
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
        if team_name == state.team_name and purpose == "Incantation" and state.level == required_level:
            print(f"Decision: Responding to incantation call for level {required_level} from direction {direction}.")
            state.is_responding_to_broadcast = True
            state.action_plan = self._get_path_from_direction(direction)
            # Look around to see if we can help
            state.action_plan.append("Look")

    def handle_server_message(self, message: str, state: PlayerState):
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
            self.pop_incantation()

            state.level_up()
            print(f"--- LEVEL UP! Now level {state.get_level()} ---")
            return

        # Fatal notification
        if message == "dead":
            state.die()
            print("--- I DIED ---")
            return

        # Handling of answers to commands
        if not self.command_queue:
            print(f"Warning: Received message '{message}' without any command in the queue. Ignoring.")
            return

        last_command = self.pop_last_command()

        # If the command failed, cancel the action plan
        if message == "ko":
            print(f"Command '{last_command}' failed.")
            state.reset_action_plan()
            return

        # If the command was successful, no need for a specific treatment
        if message == "ok":
            return

        # If the command was "Inventory" or "Look", we parse the message
        match last_command:
            case "Inventory":
                parse_inventory(message, state)
            case"Look":
                parse_look(message, state)
            case "Connect_nbr":
                print(f"Available connection slots: {message}")
            case "Fork":
                print("Successfully laid an egg!")
            case _: # Weird case where we receive an unexpected answer for a known command. This should not happen.
                print(f"WARNING: Received unexpected answer '{message}' for command '{last_command}'.")

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

    def pop_incantation(self):
        try:
            incantation_index = self.command_queue.index("Incantation")
            self.command_queue.pop(incantation_index)  # Remove the incantation command and its dependencies
        except (ValueError, IndexError):
            pass  # In case "Incantation" is not in the queue, we ignore it

    def pop_last_command(self):
        return self.command_queue.pop(0) if self.command_queue else ""

    def get_last_command(self):
        return self.command_queue[0] if self.command_queue else ""
