from MonteCarlo import MonteCarloTrainer
import pandas as pd
import numpy as np
from pickle import dump

if __name__ == '__main__':
    bins = pd.IntervalIndex.from_tuples(
        [(0, 50), (50, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 90), (90, 200)], closed="left")
    data_path = "../processed/RNLData/full_eICU_bps_with_doses.csv"
    gamma = 0.9
    epsilon = 0.2
    all_possible_actions = np.arange(0, 0.4, 0.01)
    n_episodes = 1000

    rnl_trainer = MonteCarloTrainer(data_path, all_possible_actions, bins, gamma, epsilon, n_episodes)
    V, policy, deltas = rnl_trainer.monte_carlo()

    dump(V, open('artifacts/V_eICU_full.pkl', 'wb'))
    dump(policy, open('artifacts/policy_eICU_full.pkl', 'wb'))
    dump(deltas, open('artifacts/deltas_eICU_full.pkl', 'wb'))
