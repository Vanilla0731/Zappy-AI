##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## rl_ai
##

import numpy as np
import copy
from . import logger, ACTIONS, RESOURCES, ELEVATION_REQUIREMENTS
from .server import ZappyServer
from .player import PlayerState
from .rl_agent import RLAgent
from .parsing import parse_inventory, parse_look

# --- Utility Functions for State and Reward ---

def vectorize_state(player: PlayerState) -> np.ndarray:
    """
    Convertthe player state in a NumPy vector.
    """
    # 1. Inventory (7 values)
    inventory_vec = [player.inventory.get(res, 0) for res in RESOURCES]
    
    # 2. Level (1 value)
    level_vec = [player.level]
    
    # 3. Vision 
    # Currently using a simplified vision vector
    # A better approach would be to use a One-Hot-Encoding
    player_count = sum([tile.count('player') for tile in player.vision])
    food_count = sum([tile.count('food') for tile in player.vision])
    vision_vec = [player_count, food_count]

    # Concat everything into a single state vector
    state_vector = np.array(inventory_vec + level_vec + vision_vec)
    state_vector = state_vector / 10.0 # Simple normalization to keep values in a reasonable range
    
    # Resizing (batch_size=1, state_size)
    return np.reshape(state_vector, [1, len(state_vector)])


class RLAI(ZappyServer, PlayerState):
    def __init__(self, host: str, port: int, team_name: str):
        ZappyServer.__init__(self, host, port)
        PlayerState.__init__(self, team_name)
        
        # Define the state size and action size
        # 7 (inventory) + 1 (level) + 2 (vision) = 10
        self.state_size = 10 
        self.action_size = len(ACTIONS)
        
        self.agent = RLAgent(self.state_size, self.action_size)
        self.batch_size = 32 # Size of the batch for training

        # Hybrid approach for the broadcasting
        self.action_plan = []
        self.is_responding_to_broadcast = False

    # Methods for the Hybrid Approach
    def _check_elevation_requirements(self) -> dict:
        """
        Check the elevation requirements for the current level.
        Returns a dictionary with resource requirements.
        """
        if self.level >= 8:
            return {}
        requirements = ELEVATION_REQUIREMENTS[self.level][1]
        missing_ressources = {}
        for stone, required_count in requirements.items():
            if self.inventory.get(stone, 0) < required_count:
                missing_ressources[stone] = required_count - self.inventory.get(stone, 0)
        return missing_ressources
    
    def _handle_broadcast(self, message: str, state=None):
        """
        Handle the broadcast message from other players.
        This method can be extended to handle specific commands.
        """
        logger.info(f"Received broadcast: {message}")
        try:
            direction_str, content = message.replace("broadcast ", "").split(",", 1)
            direction = int(direction_str)
            content = content.strip()

            team_name, purpose, level_str = content.split(":")
            required_level = int(level_str)
        except (ValueError, IndexError):
            logger.warning("Invalid broadcast format. Expected 'broadcast <direction>, <team_name>:<purpose>:<level>'.")
            return
        
        if (direction != 0 and
            team_name == self.team_name and
            purpose == "Incantation" and
            self.level >= required_level and
            not self.is_responding_to_broadcast):
            logger.info(f"Responding to broadcast from {team_name} for incantation at level {required_level}.")
            self.is_responding_to_broadcast = True
            self.action_plan = self._get_path_from_direction(direction)
            self.action_plan.append("Look")  # Look after reaching the destination:

    # Methods for the RL AI
    def compute_reward(self, prev_state: PlayerState, action_result: str):
        """
        Compute the reward based on the previous state, current state, and action result.
        """
        # Default reward is negative to encourage efficiency
        reward = -0.1 # Life cost for each action taken

        if self.level > prev_state.level:
            reward += 20.0 # Great reward for leveling up
            logger.info("REWARD: Level up! +20")

        # Compare l'inventaire
        for res in RESOURCES:
            diff = self.inventory.get(res, 0) - prev_state.inventory.get(res, 0)
            if diff > 0:
                reward += 1.0 # Reward for collecting resources
                logger.info(f"REWARD: Picked up {res}! +1.0")
        
        if not self.is_alive:
            reward -= 10.0 # Great penalty for dying
            logger.info("REWARD: Died! -10.0")
            
        if action_result == "ko":
            reward -= 0.5 # Penalty for failed action
            logger.info("REWARD: Action failed! -0.5")
            
        return reward

    def run(self):
        """
        Main loop for the RL AI client.
        """
        try:
            self.connect_to_server()
            width, height = self.initial_connection(self.team_name)
            self.set_world_size(width, height)

            # Infinite loop for the RL agent
            while self.is_alive:
                # Check for the action plan | Hybrid Approach
                if self.action_plan:
                    next_action = self.action_plan.pop(0)
                    self.send_command(next_action)
                    response = self.read_from_server()
                    self.handle_server_message(response)
                    if not self.action_plan:
                        self.is_responding_to_broadcast = False
                    continue # Skip the RL logic for this iteration
                # If no action plan, proceed with the RL logic
                # 1. Get the current state and vectorize it
                # Vision and Inventory updated to ensure a stable state
                self.send_command_immediately("Look")
                parse_look(self.read_from_server(), self)
                self.send_command_immediately("Inventory")
                parse_inventory(self.read_from_server(), self)
                
                prev_state_obj = copy.deepcopy(self) # Saving the previous state object
                self.handle_server_message(self.read_from_server()) # Handle any server messages
                current_state_vec = vectorize_state(self)

                # Check if the player should broadcast for an incantation
                missing_stones = self._check_elevation_requirements()
                players_needed = ELEVATION_REQUIREMENTS[self.level][0]
                players_on_tile = self.vision[0].count('player') if self.vision else 0

                if not missing_stones and players_on_tile < players_needed:
                    message = f"{self.team_name}:Incantation:{self.level}"
                    self.send_command(f"Broadcast {message}")
                    self.handle_server_message(self.read_from_server())
                    continue # Skip the RL logic for this iteration

                # 2. Choose an action using the RL agent
                action_idx = self.agent.act(current_state_vec)
                action_str = ACTIONS[action_idx]
                
                # 3. Perform the action & get the result
                self.send_command(action_str)
                action_result = self.read_from_server()
                self.handle_server_message(action_result) # Handle basics answers
                
                # 4. Get the next state after the action
                done = not self.is_alive # End of episode if the player is dead
                next_state_vec = vectorize_state(self)
                reward = self.compute_reward(prev_state_obj, action_result)
                # Only remember the experience if the action was not part of the action_plan
                self.agent.remember(current_state_vec, action_idx, reward, next_state_vec, done)
                self.agent.replay(self.batch_size)

        except KeyboardInterrupt:
            logger.info("Training interrupted. Saving the model...")
            self.agent.save(f"./zappy_ai_model_{self.team_name}.h5")
        finally:
            self.close_sock()
    
    def handle_server_message(self, message: str, state=None):
        """
        Handle the server message and update the player state accordingly.
        """
        if message.startswith("broadcast"):
            self._handle_broadcast(message)
        elif message.startswith("["):
            if self.get_last_command() == "Look":
                parse_look(message, self)
            else:
                parse_inventory(message, self)
        elif message.startswith("Current level:"):
            self.level_up()
        elif message.startswith("dead"):
            self.die()
            
        if self.command_queue:
            self.command_queue.pop(0)
        