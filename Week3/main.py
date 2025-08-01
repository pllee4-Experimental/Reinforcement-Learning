import gymnasium as gym
import ale_py
import numpy as np
from collections import namedtuple
import collections
import time
import math

import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn import Parameter, init
from torch.nn import functional as F

from tensorboardX import SummaryWriter

# Register ALE environments FIRST
gym.register_envs(ale_py)

import atari_wrappers
from agent import DQNAgent
import utils

DQN_HYPERPARAMS = {
	'dueling': False,
	'noisy_net': False,
	'double_DQN': False,
	'n_multi_step': 2,
	'buffer_start_size': 10001,
	'buffer_capacity': 15000,
	'epsilon_start': 1.0,
	'epsilon_decay': 10**5,
	'epsilon_final': 0.02,
	'learning_rate': 5e-5,
	'gamma': 0.99,
	'n_iter_update_target': 1000
}

BATCH_SIZE = 32
MAX_N_GAMES = 3000
TEST_FREQUENCY = 10

ENV_NAME = "ALE/Pong-v5"  # This works!
SAVE_VIDEO = True
DEVICE = 'cuda' # or 'cuda'
SUMMARY_WRITER = True

LOG_DIR = 'content/runs'
name = '_'.join([str(k)+'.'+str(v) for k,v in DQN_HYPERPARAMS.items()])
name = 'prv'

if __name__ == '__main__':
    print(f"Using environment: {ENV_NAME}")
    
    # create the environment
    env = atari_wrappers.make_env(ENV_NAME)
    
    if SAVE_VIDEO:
        # save the video of the games
        try:
            env = gym.wrappers.RecordVideo(env, "main-"+ENV_NAME.replace('/', '_'), episode_trigger=lambda x: True)
        except Exception as e:
            print(f"Warning: Could not set up video recording: {e}")
    
    obs, _ = env.reset()

    # TensorBoard
    writer = SummaryWriter(log_dir=LOG_DIR+'/'+name + str(time.time())) if SUMMARY_WRITER else None

    print('Hyperparams:', DQN_HYPERPARAMS)

    # create the agent
    agent = DQNAgent(env, device=DEVICE, summary_writer=writer, hyperparameters=DQN_HYPERPARAMS)

    n_games = 0
    n_iter = 0

    # Play MAX_N_GAMES games
    while n_games < MAX_N_GAMES:
        # act greedy
        action = agent.act_eps_greedy(obs)

        # one step on the environment
        new_obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        # add the environment feedback to the agent
        agent.add_env_feedback(obs, action, new_obs, reward, done)

        # sample and optimize NB: the agent could wait to have enough memories
        agent.sample_and_optimize(BATCH_SIZE)

        obs = new_obs
        if done:
            n_games += 1

            # print info about the agent and reset the stats
            agent.print_info()
            agent.reset_stats()

            #if n_games % TEST_FREQUENCY == 0:
            #	print('Test mean:', utils.test_game(env, agent, 1))

            obs, _ = env.reset()

    if writer:
        writer.close()