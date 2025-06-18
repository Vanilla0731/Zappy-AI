##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## AI
##

import sys
from typing import Any
from .decision_engine import DecisionEngine

class ZappyAI(DecisionEngine):
    def __init__(self, host: str, port: int, team_name: str, **kwargs: dict[str, Any]):
        DecisionEngine.__init__(self, host=host, port=port, team_name=team_name)

    def run(self):
        """
        Main loop for the AI client.
        """
        self.connect_to_server()
        self.initial_connection(self)
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
                message = self.read_from_server()
                print(f"Server -> Me: {message}")
                self.handle_server_message(message, self)

            except KeyboardInterrupt:
                print("\rUser interruption. Closing connection.")
                break
            except Exception as e:
                print(f"An error occurred in the main loop: {e}", file=sys.stderr)
                break

        if self.sock:
            self.sock.close()
            print("Socket closed.")
