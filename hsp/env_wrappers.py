import time
import numpy as np
import torch
import os
from mazebase.torch_featurizers import GridFeaturizer
from utils import merge_stat

import gym
import gym_minigrid.wrappers as wrappers



def MinigridWrapper(env_name):
    #env = create_env(env_name)
    env = gym.make(env_name)
    env = wrappers.FullyObsWrapper(env)
    env = Minigrid2Image(env)
    return env

def create_env(env_name):
    return Minigrid2Image(gym.make(env_name))


class Minigrid2Image(gym.ObservationWrapper):
    # FIXME: we need to support complex observation spaces
    def __init__(self, env):
        gym.ObservationWrapper.__init__(self, env)
        self.env = env
        self.observation_space = env.observation_space.spaces["image"]

        ##ANDRES
        self.observation_dim = self.env.width*self.env.height*3
        self.num_actions = self.action_space.n
        self.dim_actions = 1

        self.current_observation = torch.Tensor([])


    def observation(self, observation):
        return observation["image"]

    def get_current_obs(self):
        return self.current_observation.view(1,-1)

    def get_state(self):
        #agent_location = torch.flatten(env_output['frame'], 2, 3)
        #agent_location = agent_location[:,:,0]
        #agent_location = (agent_location == 10).nonzero() #select object id
        #agent_location = agent_location[:,2]
        #agent_location = agent_location.view(agent_output["action"].shape)
        return None

    def step(self, action):
        frame, reward, done, _ = self.env.step(action[0])
        frame = torch.Tensor(frame["image"])
        self.current_observation = frame
        return frame, reward, done, _

    def reset(self):
        frame = self.env.reset()
        frame = torch.Tensor(frame["image"])
        self.current_observation = frame
        return frame  

    def get_stat(self):
        stat = self.stat if hasattr(self, 'stat') else dict()
        if hasattr(self.env, 'get_stat'):
            merge_stat(self.env.get_stat(), stat)
        elif hasattr(self.env, 'stat'):
            merge_stat(self.env.stat, stat)
        return stat


    def set_state_id(self, id):
        if hasattr(self.env, 'set_state_id'):
            return self.env.set_state_id(id)
        else:
            return None

    def get_state_color(self):
        if hasattr(self.env, 'get_state_color'):
            return self.env.get_state_color()
        else:
            return None

    def reset_stat(self):
        if hasattr(self.env, 'reset_stat'):
            self.env.reset_stat()

    def call_recursive(self, func_name, args, defaul_val=None):
        if hasattr(self, func_name):
            return getattr(self, func_name)
        elif hasattr(self.env, func_name):
            return getattr(self.env, func_name)
        elif hasattr(self.env, 'call_recursive'):
            return self.env.call_recursive(func_name, args, defaul_val)
        else:
            return defaul_val

    def property_recursive(self, property_name, defaul_val=None):
        if hasattr(self, property_name):
            return getattr(self, property_name)
        elif hasattr(self.env, property_name):
            return getattr(self.env, property_name)
        elif hasattr(self.env, 'property_recursive'):
            return self.env.property_recursive(property_name, defaul_val)
        else:
            return defaul_val


    #def observation_dim(self):
    #    return sum(list(self.env.observation_space.shape))    





class EnvWrapper(object):
    def __init__(self, env):
        self.env = env
        if hasattr(env, 'attr'):
            self.attr = env.attr
        else:
            self.attr = dict()

    @property
    def observation_dim(self):
        return self.env.observation_dim

    @property
    def num_actions(self):
        return self.env.num_actions

    @property
    def dim_actions(self):
        return self.env.dim_actions

    @property
    def action_space(self):
        return self.env.action_space

    def reset(self):
        return self.env.reset()

    def step(self, action):
        return self.env.step(action)

    def display(self):
        self.env.display()

    def get_current_obs(self):
        return self.env.get_current_obs()

    def get_stat(self):
        stat = self.stat if hasattr(self, 'stat') else dict()
        if hasattr(self.env, 'get_stat'):
            merge_stat(self.env.get_stat(), stat)
        elif hasattr(self.env, 'stat'):
            merge_stat(self.env.stat, stat)
        return stat

    def get_state(self):
        return self.env.get_state()

    def set_state(self, state):
        self.env.set_state(state)

    def set_state_id(self, id):
        if hasattr(self.env, 'set_state_id'):
            return self.env.set_state_id(id)
        else:
            return None

    def get_state_color(self):
        if hasattr(self.env, 'get_state_color'):
            return self.env.get_state_color()
        else:
            return None

    def reset_stat(self):
        if hasattr(self.env, 'reset_stat'):
            self.env.reset_stat()

    def call_recursive(self, func_name, args, defaul_val=None):
        if hasattr(self, func_name):
            return getattr(self, func_name)
        elif hasattr(self.env, func_name):
            return getattr(self.env, func_name)
        elif hasattr(self.env, 'call_recursive'):
            return self.env.call_recursive(func_name, args, defaul_val)
        else:
            return defaul_val

    def property_recursive(self, property_name, defaul_val=None):
        if hasattr(self, property_name):
            return getattr(self, property_name)
        elif hasattr(self.env, property_name):
            return getattr(self.env, property_name)
        elif hasattr(self.env, 'property_recursive'):
            return self.env.property_recursive(property_name, defaul_val)
        else:
            return defaul_val

class RLLabWrapper(EnvWrapper):
    def __init__(self, env):
        super(RLLabWrapper, self).__init__(env)

    @property
    def observation_dim(self):
        return self.env.observation_space.shape[0]

    @property
    def num_actions(self):
        return 0 # contineous action

    @property
    def dim_actions(self):
        return self.env.action_space.shape[0]

    def reset(self):
        obs = self.env.reset()
        obs = torch.from_numpy(obs).view(1, -1)
        return obs

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        obs = torch.from_numpy(obs).view(1, -1)
        return obs, reward, done, info

    def display(self):
        if hasattr(self.env, 'render'):
            self.env.render()

    def get_current_obs(self):
        obs = self.env.get_current_obs()
        obs = torch.from_numpy(obs).view(1, -1)
        return obs


class MazeBaseWrapper(EnvWrapper):
    def __init__(self, name, game, config):
        opts = config.get_opts()
        game_opts = opts['game_opts']
        max_h = game_opts['map_height'].max_possible()
        max_w = game_opts['map_width'].max_possible()
        featurizer_opts = {'egocentric_coordinates':False,
            'max_map_sizes': (max_w, max_h)}
        opts['featurizer'] = featurizer_opts
        self.factory = game.Factory(name, opts, game.Game)
        self.featurizer = GridFeaturizer(featurizer_opts, self.factory.dictionary)
        env = self.factory.init_random_game()
        super(MazeBaseWrapper, self).__init__(env)

    @property
    def observation_dim(self):
        obs = self.get_current_obs()
        return obs.numel()

    @property
    def num_actions(self):
        return len(self.factory.actions)

    @property
    def dim_actions(self):
        return 1

    def get_current_obs(self):
        obs = self.featurizer.to_tensor(self.env, self.env.agent)
        obs = obs.view(1, -1)
        return obs

    def reset(self):
        self.env = self.factory.init_random_game()
        return self.get_current_obs()

    def step(self, action):
        action = self.factory.iactions[action[0]]
        self.env.act(action)
        self.env.update()
        obs = self.get_current_obs()
        done = not self.env.is_active()
        r = self.env.get_reward()
        return (obs, r, done, dict())

    def display(self):
        self.env.display_ascii()
        time.sleep(0.5)
