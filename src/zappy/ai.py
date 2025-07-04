##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## AI
##

from . import logger
from .decision_engine import DecisionEngine

class ZappyAI(DecisionEngine):
    def __init__(self, host: str, port: int, team_name: str) -> None:
        DecisionEngine.__init__(self, host=host, port=port, team_name=team_name)

    def run(self) -> bool:
        """
        Main loop for the AI client.
        """
        ret = False
        try:
            self.connect_to_server()
            width, heigth = self.initial_connection(self.team_name)
            self.set_world_size(width, heigth)
            self.send_command("Inventory")

            while self.is_alive:
                if not self.command_queue and not self.action_plan:
                        self.send_command("Inventory")
                        self.make_decision()

                while self.action_plan and len(self.command_queue) < 10:
                    if not self.can_send_action_plan_command(self.action_plan[0]):
                        break
                    next_action = self.action_plan.pop(0)
                    self.send_command(next_action)

                # Waiting for server answers
                message = self.read_from_server()
                logger.debug(f"Server -> Me: {message}")
                self.handle_server_message(message, self)
                if (self.timer_fork > 0):
                    self.timer_fork = self.timer_fork - 1
        except KeyboardInterrupt:
            logger.info("User interruption. Closing connection.")
            ret = True
        finally:
            self.close_sock()
        return ret
