# From The School of AI's Move 37 Course https://www.theschool.ai/courses/move-37-course/
# Coding demo by Colin Skow
# Forked from https://github.com/lazyprogrammer/machine_learning_examples/tree/master/rl
# Credit goes to LazyProgrammer
from __future__ import print_function, division
from builtins import range
from tkinter import S

import numpy as np
import matplotlib.pyplot as plt
from patient_simulator import PatientSimulator
from tqdm import tqdm


class MonteCarloTrainer:
    def __init__(self, data_path, all_possible_actions, bins, gamma=0.9, epsilon=0.2, n_episodes=1000):
        self.gamma = gamma
        self.epsilon = epsilon
        self.n_episodes = n_episodes
        self.all_possible_actions = all_possible_actions
        self.bins = bins
        self.data_path = data_path

    @staticmethod
    def max_dict(d):
        max_key = None
        max_val = float('-inf')
        for k, v in d.items():
            if v > max_val:
                max_val = v
                max_key = k
        return max_key, max_val

    def epsilon_action(self, a, eps=0.1):
        p = np.random.random()
        if p < (1 - eps):
            return a
        else:
            return np.random.choice(self.all_possible_actions)

    def init_policy(self):
        policy = {}
        for s in self.bins:
            policy[str(s)] = np.random.choice(self.all_possible_actions)
        return policy

    def play_game(self, policy):
        # returns a list of states and corresponding returns
        patient = PatientSimulator(data_path=self.data_path, bins=self.bins)
        s = patient.bp_category
        a = self.epsilon_action(policy[s], self.epsilon)

        # keep in mind that reward is lagged by one time step
        # r(t) results from taking action a(t-1) from s(t-1) and landing in s(t)
        states_actions_rewards = [(s, a, 0)]
        while True:
            s, r = patient.move(a)
            if patient.game_over():
                break
            else:
                if str(s) == 'nan':
                    print("patient nan recieved")
                    patient.game_over = True
                    break
                try:
                    a = self.epsilon_action(policy[s], self.epsilon)
                except KeyError:
                    print(f"catched KeyError s={s}")
                    break
                states_actions_rewards.append((s, a, r))

        G = 0
        states_actions_returns = []
        first = True
        for s, a, r in reversed(states_actions_rewards):
            if first:
                first = False
            else:
                states_actions_returns.append((s, a, G))
            G = r + self.gamma * G
        states_actions_returns.reverse()  # back to the original order of states visited
        return states_actions_returns

    def monte_carlo(self):
        policy = self.init_policy()
        Q = {}
        returns = {}
        states = self.bins
        for s in states:
            Q[str(s)] = {}
            for a in self.all_possible_actions:
                Q[str(s)][a] = 0
                returns[(str(s), a)] = []

        # keep track of how much our Q values change each episode so we can know when it converges
        deltas = []
        # repeat for the number of episodes specified (enough that it converges)
        for t in tqdm(range(self.n_episodes)):
            # generate an episode using the current policy
            biggest_change = 0
            states_actions_returns = self.play_game(policy)

            # calculate Q(s,a)
            seen_state_action_pairs = set()
            for s, a, G in states_actions_returns:
                # check if we have already seen s
                # first-visit Monte Carlo optimization
                sa = (s, a)
                if sa not in seen_state_action_pairs:
                    returns[sa].append(G)
                    old_q = Q[s][a]
                    # the new Q[s][a] is the sample mean of all our returns for that (state, action)
                    Q[s][a] = np.mean(returns[sa])
                    biggest_change = max(biggest_change, np.abs(old_q - Q[s][a]))
                    seen_state_action_pairs.add(sa)
            deltas.append(biggest_change)

            # calculate new policy pi(s) = argmax[a]{ Q(s,a) }
            for s in policy.keys():
                a, _ = MonteCarloTrainer.max_dict(Q[s])
                policy[s] = a

        # calculate values for each state (just to print and compare)
        # V(s) = max[a]{ Q(s,a) }
        V = {}
        for s in policy.keys():
            V[s] = MonteCarloTrainer.max_dict(Q[s])[1]

        return V, policy, deltas
