import pandas as pd
import numpy as np

TARGET_BP = 65
np.random.seed(42)


def add_first_and_last_indicators(df):
    # add first and last indicators
    # sort by stay_id and cur_bp_time
    df = df.sort_values(["stay_id", "cur_bp_time"], ascending=False)
    df["last"] = df.groupby("stay_id").cumcount() == 0
    df = df.sort_values(["stay_id", "cur_bp_time"], ascending=True)
    df["first"] = df.groupby("stay_id").cumcount() == 0

    # get last bp of each stay indicator
    return df


class PatientSimulator:
    def __init__(self, data_path, bins, nor_eps=0.01):
        self.df = pd.read_csv(data_path)
        self.bp, self.bp_category = self.__get_random_init_bp()
        self.nor_eps = nor_eps
        self.bins = bins

    def __get_random_init_bp(self):
        # get random bp from samples who are marked first
        first_bp_per_stay = self.df[self.df["first"]].sample(1)
        return first_bp_per_stay["cur_bp"].values[0], first_bp_per_stay["bp_category"].values[0]

    def __get_square_dist_from_target(self):
        return - ((self.bp - TARGET_BP) ** 2)

    def move(self, dose):
        """
        :param dose: NOR dosage given by caretaker
        :return: the reward for the dose
        """
        # get original_rates with distance epsilon from dose
        original_rates_eps = self.df[(self.df.dose >= dose - self.nor_eps) & (self.df.dose <= dose + self.nor_eps)]
        # get the original_rates with the same bp category
        original_rates_eps_bp = original_rates_eps[original_rates_eps.bp_category == self.bp_category]
        new_bp_row = original_rates_eps_bp.sample(1) if len(original_rates_eps_bp) > 0 else self.df.sample(1)
        # update the current bp
        self.bp = new_bp_row.next_bp.values[0]
        self.bp_category = new_bp_row.next_bp_category.values[0]
        self.is_game_over = new_bp_row["last"].values[0]
        if self.bp <= 0:
            self.bp = 0
            self.is_game_over = True
            self.bp_category = self.bins[0]

        # return the new state and reward
        return self.bp_category, self.__get_square_dist_from_target()
        
    def game_over(self):
        return self.is_game_over