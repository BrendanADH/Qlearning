#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 17:34:45 2023

@author: brendandevlin-hill
"""

#%%

import pandas as pd
import numpy as np
import os
import random
import GridLearning as gl


# data directory
data_directory = os.getcwd() + "/data/"

# import a pkl of the normalised energy deposition
# intQ = pd.read_pickle(data_directory + "rects_id12_integratedQ.pkl")


# create the q table. 
# each row corresponds to a system state.
# each column corresponds to the quality score of the actions
# actions are wait/move cw/move ccw/inspect

#%%

print("Generating states...")

# generate a 2d grid
grid_size = 4
goal_position = np.array([[1,1]])

states = []
states_dict = {}
counter = 0

for y in range(0, grid_size):
    for x in range(0, grid_size):
        states.append(([x,y]))
        states_dict[str(np.array([x,y]))] = counter
        counter += 1

states = np.array(states)

#%%

# define possible state transitions. [state, state, state, state...]
# the row index corresponds to the outgoing state
# the column index corresponds to the action taken
# the contents of [i,j] corresponds to the index of the resultant state

def isAinB(a,b):
    for entry in b:
        if entry[0] == a[0] and entry[1] == a[1]:
            return True
    return False
            
def GenerateTransitions(goal_position):   
    
    goal_position = np.array(goal_position)    
    transitions = np.zeros((len(states),4))
    transition_rewards = np.zeros((len(states),4))

    for i in range(len(states)):
        
        available_states = np.ones((4))*-1
        available_rewards = np.zeros(4)
        
        if states[i,0]>0: #left 
            new_state = states[i] - [1,0]
            new_state_index = states_dict[str(new_state)]
            available_states[0] = new_state_index
            if (states_dict[str(goal_position)] == new_state_index):
                available_rewards[0] = 1
            
        if states[i,0]<(grid_size-1): #right 
            new_state = states[i] + [1,0]
            new_state_index = states_dict[str(new_state)]
            available_states[1] = new_state_index
            if (states_dict[str(goal_position)] == new_state_index):
                available_rewards[1] = 1
            
        if states[i,1]>0: #down
            new_state = states[i] - [0,1]
            new_state_index = states_dict[str(new_state)]
            available_states[2] = new_state_index
            if (states_dict[str(goal_position)] == new_state_index):
                available_rewards[2] = 1
            
        if states[i,1]<(grid_size-1): #up 
            new_state = states[i] + [0,1]
            new_state_index = states_dict[str(new_state)]
            available_states[3] = new_state_index
            if (states_dict[str(goal_position)] == new_state_index):
                available_rewards[3] = 1
            
        transitions[i] = available_states
        transition_rewards[i] = available_rewards
        
    return transitions, transition_rewards
        
#%%

def DistReward(system, state, action):
    
    goal_position = system.goal_position
    diff = goal_position - state
    diff = [abs(e) for e in diff]
    
    return 5/(np.sum(diff)+1)


goal_A = [2,2]
trans_A, rewards_A = GenerateTransitions(goal_A)

Qtable = np.random.rand(*np.shape(trans_A))
Qtable = Qtable + (trans_A < 0) * -1e9

agent_A = gl.TrainGrid(qtable = Qtable, 
                    system = gl.GridSystem(states, goal_A, states, states_dict, trans_A, rewards_A, DistReward),
                    max_steps = 50,
                    n_training_episodes = 200000, #1E+7 and 3E-7 decay rate work together nicely
                    min_epsilon = 0.05,
                    max_epsilon = 0.5,
                    decay_rate = 0.000001, #3E-6,
                    gamma = 0.7,
                    learning_rate = 0.2)

goal_B = [3,3]
trans_B, rewards_B = GenerateTransitions(goal_B)

Qtable = np.random.rand(*np.shape(trans_B))
Qtable = Qtable + (trans_B < 0) * -1e9

agent_B = gl.TrainGrid(qtable = Qtable, 
                    system = gl.GridSystem(states, goal_B, states, states_dict, trans_B, rewards_B, DistReward),
                    max_steps = 50,
                    n_training_episodes = 200000, #1E+7 and 3E-7 decay rate work together nicely
                    min_epsilon = 0.05,
                    max_epsilon = 0.5,
                    decay_rate = 0.000001, #3E-6,
                    gamma = 0.7,
                    learning_rate = 0.2)



#%%

compound_agent = agent_A + agent_B
compound_agent = (compound_agent > 0) * compound_agent

trans_test, rewards_test = GenerateTransitions([2,2])

ev = gl.EvaluateGrid(qtable = compound_agent,
                     system = gl.GridSystem(states, goal_position[0], states, states_dict, transitions, transition_rewards, DistReward),
                     n_eval_episodes=10000,
                     max_steps=40,
                     gamma=0.7)



#%%


def DistReward(system, state, action):
    
    goal_position = system.goal_position
    diff = goal_position - state
    diff = [abs(e) for e in diff]

    
    return 5/(np.sum(diff)+1)

agent = gl.TrainGrid(qtable = compound_agent, 
                    system = gl.GridSystem(states, goal_position[0], states, states_dict, transitions, transition_rewards, DistReward),
                    max_steps = 50,
                    n_training_episodes = 200000, #1E+7 and 3E-7 decay rate work together nicely
                    min_epsilon = 0.05,
                    max_epsilon = 0.5,
                    decay_rate = 0.000001, #3E-6,
                    gamma = 0.7,
                    learning_rate = 0.2)












