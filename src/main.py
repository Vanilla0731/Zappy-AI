##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## main
##

import sys
import argparse
import socket

class ZappyAI:
    def __init__(self, host: str, port: int, team_name: str):
        self.host = host
        self.port = port
        self.team_name = team_name
        self.sock = None
        self.buffer = ""


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
        """Waits for 'WELCOME' and sends the team name."""
        welcome_message = self._read_from_server()
        if welcome_message != "WELCOME":
            print(f"Error: Expected 'WELCOME' from server, but got '{welcome_message}'", file=sys.stderr)
            sys.exit(84)
        
        print(f"Server -> Me: {welcome_message}")
        
        print(f"Me -> Server: {self.team_name}")
        if self.sock is not None:
            self.sock.sendall(f"{self.team_name}\n".encode('utf-8'))
        else:
            print("Error: Socket is not connected.", file=sys.stderr)
            sys.exit(1)


    def run(self):
        """Main loop for the AI client."""
        self.connect_to_server()
        self._initial_connection()

        while True:
            try:
                message = self._read_from_server()
                print(f"Server -> Me: {message}")
                
                # --- IMPLEMENT AI LOGIC HERE ---
                
            except KeyboardInterrupt:
                print("\nUser interruption. Closing connection.")
                break
            except Exception as e:
                print(f"An error occurred in the main loop: {e}", file=sys.stderr)
                break
        
        if self.sock:
            self.sock.close()
            print("Socket closed.")

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
