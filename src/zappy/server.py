##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## server
##

import sys
import socket

class ZappyServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = None
        self.buffer = ""
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

    def get_command_queue(self):
        return self.command_queue

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
