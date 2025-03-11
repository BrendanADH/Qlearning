import numpy as np
import math


def exponential_epsilon_decay(episode, epsilon_max, epsilon_min, max_epsilon_time, min_epsilon_time, num_episodes,
                              decay_rate=None):
    if (not decay_rate):
        decay_rate = np.log(100 * (epsilon_max - epsilon_min)) / (
                num_episodes - (max_epsilon_time + min_epsilon_time))  # ensures epsilon ~= epsilon_min at end

    if (episode < max_epsilon_time):
        # print("max ep")
        epsilon = epsilon_max
    elif (episode > num_episodes - min_epsilon_time):
        epsilon = epsilon_min
    else:
        # print("decaying ep")
        decay_term = math.exp(-1. * (episode - max_epsilon_time) * decay_rate)
        epsilon = epsilon_min + (epsilon_max - epsilon_min) * decay_term

    return epsilon


def linear_epsilon_decay(episode, epsilon_max, epsilon_min, max_epsilon_time, min_epsilon_time, num_episodes):
    gradient = (epsilon_min - epsilon_max) / (num_episodes - max_epsilon_time - min_epsilon_time)

    if (episode < max_epsilon_time):
        epsilon = epsilon_max
    elif (episode > num_episodes - min_epsilon_time):
        epsilon = epsilon_min
    else:
        epsilon = epsilon_max + (gradient * (episode - max_epsilon_time))

    return epsilon
