##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## server
##

import sys
import socket
from .player import PlayerState
from .exception import ZappyError
from . import logger, ACTION_SPEED
from .parsing import parse_inventory, parse_look

class ZappyServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = ""
        self.command_queue: list[str | None] = []
        self.sent_commands: list[str | None] = []

    @staticmethod
    def _get_path_from_direction(direction: int) -> (list | list[str]):
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

    def initial_connection(self, team_name: str) -> tuple[int, int]:
        """
        Waits for 'WELCOME' and sends the team name.
        """
        welcome_message = self.read_from_server()
        if welcome_message != "WELCOME":
            raise ZappyError("initial_connection", f"Expected 'WELCOME' from server, but got '{welcome_message}'.")

        logger.debug(f"Server -> Me: {welcome_message}")
        logger.debug(f"Me -> Server: {team_name}")
        self.send_command_immediately(f"{team_name}")

        client_num_str = self.read_from_server()
        if client_num_str == "ko":
            raise ZappyError("initial_connection", "Team can't have more members")

        world_size_str = self.read_from_server()
        logger.debug(f"Server -> Me: {world_size_str}")
        width, heigth = map(int, world_size_str.split())
        logger.info(f"World size: {width}x{heigth}")
        return width, heigth

    def connect_to_server(self) -> None:
        """
        Create the socket(s) and connect to the Zappy server.
        """
        logger.info(f"Trying to connect to Zappy server at {self.host}:{self.port}...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info("Connection established with Zappy server.")

        except ConnectionRefusedError:
            raise ZappyError("connect_to_server", "Connection denied.")
        except socket.timeout:
            raise ZappyError("connect_to_server", "No response from the server (timeout).")

    def read_from_server(self) -> str:
        """
        Reads from the server buffer until a newline character is found.
        """
        while "\n" not in self.buffer:
            if self.sock is None:
                raise ZappyError("read_from_server", "Socket is not connected.")
            data = self.sock.recv(1024).decode('utf-8')
            if not data:
                logger.info("Connection closed by the server.")
                sys.exit(0)
            self.buffer += data

        line, self.buffer = self.buffer.split("\n", 1)
        return line

    def _handle_broadcast(self, message: str, state: PlayerState) -> None:
        """
        Parses and reacts to a broadcast message from another player.
        Exemple de message du serveur: "message 2, NOM_EQUIPE:incantation:4"
        """
        logger.info(f"Broadcast received: {message}")
        try:
            # Format: "message K, text"
            direction_str, content = message.replace("message ", "").split(",", 1)
            direction = int(direction_str)
            content = content.strip()
        except ValueError:
            logger.warning(f"Could not parse broadcast: {message}")
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
            logger.warning(f"Could not parse broadcast: {message}")
            return

        # 3. Check if the message is relevant to us
        logger.debug(f"Check value Name :")
        logger.debug(f"valueBase : {team_name} tested value : {state.team_name}")
        logger.debug(f"Purpose : Incantation == {purpose}")
        logger.debug(f"state level : {state.level} tested value : {required_level}")
        if purpose == "Incantation" and state.level == required_level:
            logger.debug(f"Decision: Responding to incantation call for level {required_level} from direction {direction}.")
            state.is_responding_to_broadcast = True
            state.action_plan = self._get_path_from_direction(direction)
            logger.debug(f"Direction ? : {direction}")
            for value in state.action_plan:
                logger.debug(f"action plan : {value}")
            state.action_plan.append("Look")    
            # Look around to see if we can help

    @staticmethod
    def find_action_index(action: str) -> int:
        for index, val in enumerate(ACTION_SPEED):
            if action in val:
                return index
        return -1

    def can_send_action_plan_command(self, command: str) -> bool:
        if not self.sent_commands:
            return True

        last_index = self.find_action_index(self.sent_commands[len(self.sent_commands) - 1])
        next_index = self.find_action_index(command.split(' ', 1)[0].lower())

        if last_index == -1 or next_index == -1:
            raise ZappyError("can_send_action_plan_command", "invalid action.")

        return next_index <= last_index


    def handle_server_message(self, message: str, state: PlayerState) -> None:
        """
        Handle messages received from the server.
        This method may be extended to handle different types of messages.
        """
        # Holding of every non-solicited messages
        if message.startswith("message"):
            if (self.sent_commands):
                self.sent_commands.pop(0)
            self._handle_broadcast(message, state)
            return

        # "Elevation underway" is a notification, we must ignore it
        if message == "Elevation underway":
            logger.info(f"An elevation ritual is underway on the tile.")
            return

        # "Current level: n" is the result of an incantation.
        if message.startswith("Current level:"):
            self.pop_incantation()
            state.level_up()
            if (self.sent_commands):
                self.sent_commands.pop(0)
            logger.info(f"--- LEVEL UP! Now level {state.get_level()} ---")
            return

        # Fatal notification
        if message == "dead":
            state.die()
            logger.warning("--- I DIED ---")
            return

        # Handling of answers to commands
        if not self.command_queue:
            return

        last_command = self.pop_last_command()

        # If the command failed, cancel the action plan
        if message == "ko":
            logger.warning(f"Command '{last_command}' failed.")
            if (self.sent_commands):
                self.sent_commands.pop(0)
            state.reset_action_plan()
            return

        # If the command was successful, no need for a specific treatment
        if message == "ok":
            if (self.sent_commands):
                self.sent_commands.pop(0)
            return

        # If the command was "Inventory" or "Look", we parse the message
        match last_command:
            case "Inventory":
                if (self.sent_commands):
                    self.sent_commands.pop(0)
                parse_inventory(message, state)
            case"Look":
                if (self.sent_commands):
                    self.sent_commands.pop(0)
                parse_look(message, state)
            case "Connect_nbr":
                if (self.sent_commands):
                    self.sent_commands.pop(0)
                logger.info(f"Available connection slots: {message}")
            case "Fork":
                if (self.sent_commands):
                    self.sent_commands.pop(0)
                logger.info("Successfully laid an egg!")
            case _: # Weird case where we receive an unexpected answer for a known command. This should not happen.
                logger.warning(f"Received unexpected answer '{message}' for command '{last_command}'.")

    def send_command_immediately(self, command: str) -> None:
        """
        Send a command without using the command queue (for initial connection).
        """
        if self.sock is not None:
            self.sock.sendall(f"{command}\n".encode('utf-8'))
        else:
            raise ZappyError("send_command_immediately", "Socket is not connected.")

    def close_sock(self) -> None:
        if self.sock:
            self.sock.close()
            logger.info("Socket closed.")

    def send_command(self, command: str) -> bool:
        """
        Add a command to the command queue and send it to the server.
        """
        if len(self.command_queue) < 10:
            logger.debug(f"Me -> Server: {command}")
            self.send_command_immediately(command)
            self.command_queue.append(command)
            self.sent_commands.append(command.split(' ', 1)[0].lower())
            return True
        logger.warning("Command queue is full. Cannot send new command yet.")
        return False

    def pop_incantation(self) -> None:
        try:
            self.command_queue.remove("Incantation")
        except ValueError:
            pass  # In case "Incantation" is not in the queue, we ignore it

    def pop_last_command(self) -> (str | None):
        return self.command_queue.pop(0) if self.command_queue else ""

    def get_last_command(self) -> (str | None):
        return self.command_queue[0] if self.command_queue else ""
