#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 11:31:21 2023

@author: brendandevlin-hill
"""

import gymnasium as gym
import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count


import Qlearning as ql
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

torch.set_grad_enabled(True)

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 128)
        self.layer2 = nn.Linear(128, 128)
        self.layer3 = nn.Linear(128, n_actions)

    # Returns the row of the qtable for this state
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)
            

class ReplayMemory(object):
    
    """
        Replay memory allows us to store a fragment of the agent's experiences.
        This can then be sampled from later for learning.
    """

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

#%%

## instantiate the tokamak environment
tokamak = gym.make("Tokamak-v1", num_robots=3, size=24, num_goals=3, goal_locations=[1,5,9])

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward')) 

n_training_episodes = int(1e6)
max_epsilon = 0.5 # exploration rate
decay_rate = 0 # decay of exploration rate
min_epsilon = 0.05
learning_rate = 0.5 # learning rate of the optimiser
gamma = 1 # discount factor

device = "cpu"

observation, info = tokamak.reset()
num_actions = tokamak.action_space.n

## initialise the DQNs
policy_DQN = DQN(len(observation), num_actions).to(device) # this will return our policy

loss_fn = nn.HuberLoss()
optimiser = optim.SGD(policy_DQN.parameters(), lr=learning_rate)
memory = ReplayMemory(10000) # initialise the replay memory, which will store transitions of the DQN(s)

#%%

done_counter_period = 0 # counts how many times the task is completed per period
period_times = [] # stores time per run, is emptied at end of episode
period_rewards = [] # stores rewards per run, is reset after 'period_length' episodes
period_length = 100 # length of the period. For diagnostics only.
max_steps = 150 # maximum steps before a run terminates

# training loop
for episode in range(n_training_episodes):

    epsilon = min_epsilon + (max_epsilon - min_epsilon) * np.exp(-decay_rate*episode)    
    episode_reward = 0
    step = 0
    done = False

    # Reset the environment
    state, info = tokamak.reset()
    state = torch.tensor(list(state.values()), dtype=torch.float32, device=device).unsqueeze(0)
    terminated = False
    
    # repeat
    while not done:
        
        step += 1
        
        ### estimate qvalues and retrieve action
        ### forbidden actions are not needed as no actions are currently forbidden
        qvalues = policy_DQN.forward(x = state) # get the qvalues based on the the current state
        action = ql.TensorEpsilonPolicy(state, policy_DQN, tokamak, epsilon, []) # find what action to take 
        observation, reward, terminated, _, info = tokamak.step(action.item()) # move the system and collect information
        episode_reward += reward # for diagnostics

        ### get the qvalues for the next state -- should probably avoid list cast for speed
        next_qvalues = policy_DQN.forward(x = torch.tensor(list(observation.values()), dtype=torch.float32,device=device).unsqueeze(0)) # 'observation' is the next state
        
        ### update the q values
        update_q = reward + gamma * next_qvalues.max()
        loss = loss_fn(qvalues.max(), update_q) # calculate the loss
        optimiser.zero_grad() # sets the gradients back to 0 before we calculate them again
        loss.backward() # back-propagate the loss through the NN -- will be picked up and used by the optimiser
        torch.nn.utils.clip_grad_value_(policy_DQN.parameters(), 100) # restricts the norm of the loss derivates of arg 1 to the value of arg 2
        optimiser.step() # optimise based on the derivative of the loss which was calculated with .backward()
        
        if (terminated):
            done_counter_period += 1
            next_state = None
            done = True
        if(step > max_steps):
            next_state = None
            done = True
        else: 
            next_state = torch.tensor(list(observation.values()), dtype=torch.float32, device=device).unsqueeze(0)
        state = next_state

    period_times.append(info["elapsed"])
    period_rewards.append(episode_reward)

    if (episode%period_length == 0):
        period_done_percent = (done_counter_period*100/period_length)
        if(episode > 0): # goes a bit weird if episode 0 is printed
            print("\nEpisode {: >5d}/{:>5d} | epsilon: {:0<7.5f} | Av. steps: {: >4.2f} | Min steps: {: >4d} | Av. reward: {: >4.6f} | Completed: {: >4.2f}%".format(episode,
                                                                                                                                        n_training_episodes,
                                                                                                                                        epsilon,
                                                                                                                                        np.mean(period_times),
                                                                                                                                        np.min(period_times),
                                                                                                                                        np.mean(period_rewards),
                                                                                                                                        period_done_percent), end="")
        done_counter_period = 0 # counts how many times the task is completed per period
        period_times = [] # stores time per run, is emptied at end of episode
        period_rewards = [] # stores rewards per run, is reset after 'period_length' episodes
        period_length = 100 # length of the period. For diagnostics only.

print("\nTraining finished.")


        
    