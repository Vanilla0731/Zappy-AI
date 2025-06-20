##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## rl_agent
##

import numpy as np
import tensorflow as tf
from collections import deque
import random

# Disable TensorFlow logging to avoid cluttering the output
tf.get_logger().setLevel('ERROR')

class RLAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        # Hyperparameters
        self.memory = deque(maxlen=2000) # Memory to store experiences
        self.gamma = 0.95    # Devaloration factor (discount rate)
        self.epsilon = 1.0   # Epsilon-greedy exploration rate
        self.epsilon_min = 0.01 # Minimum exploration rate
        self.epsilon_decay = 0.995 # Speed of decay of the exploration rate
        self.learning_rate = 0.001
        
        self.model = self._build_model()

    def _build_model(self):
        """
        Building the neural network model for the agent.
        """
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.state_size,)),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), 
                      loss='mse')
        return model

    def remember(self, state, action, reward, next_state, done):
        """
        Store an experience in memory.
        """
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        Choose an action based on the current state using epsilon-greedy policy.
        """
        if np.random.rand() <= self.epsilon:
            # Exploration: random action
            return random.randrange(self.action_size)
        # Exploitation: predict the best action using the model
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])

    def replay(self, batch_size):
        """
        Train the model using a batch of experiences from memory.
        """
        if len(self.memory) < batch_size:
            return # Not enough experiences to sample from
            
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                # Bellman equation: target = reward + gamma * max(Q(next_state, a))
                target = (reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0]))
            
            # Target for the current state-action pair
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            
            # Train the model on the current state
            self.model.fit(state, target_f, epochs=1, verbose=0)
            
        # Reduce epsilon after each replay to decrease exploration over time
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        """
        Load the weights of the model from a file.
        """
        self.model.load_weights(name)

    def save(self, name):
        """
        Save the weights of the model to a file.
        """
        self.model.save_weights(name)