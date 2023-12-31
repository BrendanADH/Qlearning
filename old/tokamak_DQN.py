#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 15:12:23 2023

@author: brendandevlin-hill
"""

import gymnasium as gym
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import torch
import DQN
import os

num_robots = 3
size = 12
goal_locations = [11,5,2,10,12,8]
goal_probabilities = [0.5, 0.9, 0.7, 0.7, 0.4, 0.7]

env_to_use = "Tokamak-v6"

env = gym.make(env_to_use,
               num_robots=num_robots,
               goal_locations=goal_locations,
               goal_probabilities=goal_probabilities,
               size=size,
               render_mode=None)
reset_options = {"robot_locations" : [1,3,5]}
# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
plt.ion()

# if GPU is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# saved_weights_name = "policy_weights_946424901"


#%%
n_actions = env.action_space.n
state, info = env.reset()
n_observations = len(state)

policy_net = DQN.DeepQNetwork(n_observations, n_actions).to(device)
try:
    assert saved_weights_name
    print("Loading from '/outputs/policy_weights_946424901'")
    policy_net.load_state_dict(torch.load(os.getcwd() + "/outputs/" + saved_weights_name))
except NameError:
    print("No saved weights defined, starting from scratch")
target_net = DQN.DeepQNetwork(n_observations, n_actions).to(device)
target_net.load_state_dict(policy_net.state_dict())


#%%
trained_dqn, dur, re, eps = DQN.train_model(env,
                                            policy_net,
                                            target_net,
                                            reset_options,
                                            alpha=1e-3,
                                            num_episodes=2000,
                                            epsilon_min=0,
                                            usePseudorewards=False,
                                            batch_size=256)

filename = f"policy_weights_{int(np.random.rand()*1e9)}"
print(f"Saving as {filename}")
torch.save(trained_dqn.state_dict(), f"./outputs/{filename}")

#%%


_ = DQN.evaluate_model(dqn=policy_net,
                       num_episodes=1000,
                       template_env=env,
                       reset_options=reset_options,
                       env_name=env_to_use,
                       render=True)
