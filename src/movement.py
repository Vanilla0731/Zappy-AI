##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## right
##

import sys
import socket

def movement_ai(sock: socket, buffer: str) -> None:
        if sock is not None:
            sock.sendall(buffer.encode('utf-8'))
        else:
            print("Error: Socket is not connected.", file=sys.stderr)
            sys.exit(1)
