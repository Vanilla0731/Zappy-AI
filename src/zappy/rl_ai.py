##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## rl_ai
##

import numpy as np
from . import logger, ACTIONS, RESOURCES
from .server import ZappyServer
from .player import PlayerState
from .rl_agent import RLAgent
from .parsing import parse_inventory, parse_look

# --- Utility Functions for State and Reward ---

def vectorize_state(player: PlayerState) -> np.ndarray:
    """Convertit l'état du joueur en un vecteur numpy."""
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
            reward -= 60.0 # Great penalty for dying
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
                # 1. Get the current state and vectorize it
                # Vision and Inventory updated to ensure a stable state
                self.send_command_immediately("Look")
                parse_look(self.read_from_server(), self)
                self.send_command_immediately("Inventory")
                parse_inventory(self.read_from_server(), self)
                
                prev_state_obj = self # Saving the previous state object
                current_state_vec = vectorize_state(self)

                # 2. Choose an action using the RL agent
                action_idx = self.agent.act(current_state_vec)
                action_str = ACTIONS[action_idx]
                
                # 3. Perform the action & get the result
                self.send_command_immediately(action_str)
                action_result = self.read_from_server()
                
                # 4. Get the next state after the action
                done = not self.is_alive # End of episode if the player is dead
                # Revise the state after the action
                self.send_command_immediately("Look")
                parse_look(self.read_from_server(), self)
                self.send_command_immediately("Inventory")
                parse_inventory(self.read_from_server(), self)
                next_state_vec = vectorize_state(self)

                # 5. Calculate the reward
                reward = self.compute_reward(prev_state_obj, action_result)
                
                # 6. Memorize the experience
                self.agent.remember(current_state_vec, action_idx, reward, next_state_vec, done)
                
                # 7. Train the agent by replaying experiences
                self.agent.replay(self.batch_size)

        except KeyboardInterrupt:
            logger.info("Training interrupted. Saving the model...")
            self.agent.save(f"./zappy_ai_model_{self.team_name}.h5")
        finally:
            self.close_sock()