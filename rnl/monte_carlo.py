# From The School of AI's Move 37 Course https://www.theschool.ai/courses/move-37-course/
# Coding demo by Colin Skow
# Forked from https://github.com/lazyprogrammer/machine_learning_examples/tree/master/rl
# Credit goes to LazyProgrammer
from __future__ import print_function, division
from builtins import range
from tkinter import S
# Note: you may need to update your version of future
# sudo pip install -U future

import numpy as np
import matplotlib.pyplot as plt
from patient_simulator import PatientSimulator
from utils import max_dict, print_values, print_policy
from rnl_consts import *
from tqdm import tqdm

GAMMA = 0.9
EPSILON=0.2
ALL_POSSIBLE_ACTIONS = np.arange(0, 0.4, 0.01)
N_EPISODES = 1000

# epsilon greedy action selection
def epsilon_action(a, eps=0.1):
  p = np.random.random()
  if p < (1 - eps):
    return a
  else:
    return np.random.choice(ALL_POSSIBLE_ACTIONS)

def play_game(policy):
  # returns a list of states and corresponding returns
  # s = (2, 0)
  # grid.set_state(s)
  patient = PatientSimulator()
  s = patient.bp_category
  a = epsilon_action(policy[s], EPSILON)

  # keep in mind that reward is lagged by one time step
  # r(t) results from taking action a(t-1) from s(t-1) and landing in s(t)
  states_actions_rewards = [(s, a, 0)]
  while True:
    s, r = patient.move(a)
    # s = grid.current_state()
    if patient.game_over():
      # states_actions_rewards.append((s, None, r))
      break
    else:
      if str(s) == 'nan':
        print("patient nan recieved")
        patient.game_over = True
        break
      try:
        a = epsilon_action(policy[s], EPSILON)
      except KeyError:
        print(f"catched KeyError s={s}")
        break
      states_actions_rewards.append((s, a, r))

  # calculate the returns by working backwards from the terminal state
  G = 0
  states_actions_returns = []
  first = True
  for s, a, r in reversed(states_actions_rewards):
    # a terminal state has a value of 0 by definition
    # this is the first state we encounter in the reversed list
    # we'll ignore its return (G) since it doesn't correspond to any move
    if first:
      first = False
    else:
      states_actions_returns.append((s, a, G))
    G = r + GAMMA*G
  states_actions_returns.reverse() # back to the original order of states visited
  return states_actions_returns


def init_random_policy():
  policy = {}
  for s in BINS: # for s in states
    policy[str(s)] = np.random.choice(ALL_POSSIBLE_ACTIONS)
  return policy

def monte_carlo():
  # initialize a random policy
  policy = init_random_policy()

  # initialize Q(s,a) and returns
  Q = {}
  returns = {} # dictionary of state -> list of returns we've received
  states = BINS
  for s in states:
    Q[str(s)] = {}
    for a in ALL_POSSIBLE_ACTIONS:
      Q[str(s)][a] = 0
      returns[(str(s),a)] = []
  
  # keep track of how much our Q values change each episode so we can know when it converges
  deltas = []
  # repeat for the number of episodes specified (enough that it converges)
  for t in tqdm(range(N_EPISODES)):
    # generate an episode using the current policy
    biggest_change = 0
    states_actions_returns = play_game(policy)

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
      a, _ = max_dict(Q[s])
      policy[s] = a
  
  # calculate values for each state (just to print and compare)
  # V(s) = max[a]{ Q(s,a) }
  V = {}
  for s in policy.keys():
    V[s] = max_dict(Q[s])[1]
  
  return V, policy, deltas


def test():
  policy = init_random_policy()
  print(f"initial policy: {policy}")
  print("starting game...")
  states_actions_returns = play_game(policy)
  print("states and actions: ", states_actions_returns)


if __name__ == '__main__':
  # test()
  # import os
  # print(os.getcwd())
  V, policy, deltas = monte_carlo()
  from pickle import dump
  dump(V, open('V.pkl', 'wb'))
  dump(policy, open('policy.pkl', 'wb'))
  dump(deltas, open('deltas.pkl', 'wb'))



# if __name__ == '__main__':
#   grid = standard_grid(obey_prob=0.9, step_cost=None)

#   # print rewards
#   print("rewards:")
#   print_values(grid.rewards, grid)

#   V, policy, deltas = monte_carlo(grid)

#   print("final values:")
#   print_values(V, grid)
#   print("final policy:")
#   print_policy(policy, grid)

#   plt.plot(deltas)
#   plt.show()
