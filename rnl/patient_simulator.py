import pandas as pd
import numpy as np

# DATA_PATH = "../processed/full_pipeline_ok_filtered.csv" #TODO: have a file with dose=0
DATA_PATH = "rnl\dummy_data\dummy_data.csv"
TARGET_BP = 65

np.random.seed(42)

class PatientSimulator:
    def __get_random_init_bp(self):
        # for each stay_id get its first bp
        first_bp_per_stay = self.df.sort_values("bp_time", ascending=True).groupby("stay_id").first()
        # get a random bp from the first bp of each stay, and category
        first_bp_per_stay = self.df.sample(1)
        # print(first_bp_per_stay.to_())
        # return the bp
        return first_bp_per_stay.cur_state, first_bp_per_stay.bp_category
    
    def __get_square_dist_from_target(self):
        return (self.bp - TARGET_BP) ** 2

    def _init_data(self):
        df = pd.read_csv(DATA_PATH)
        self.df = df[(df.cur_state > 0) & (df.cur_state < 200)] #TODO: do it in the preprocessing
        # get bins for dose and bp
        category_series= pd.cut(self.df.cur_state, bins=10)
        # set name to category
        category_series.name = "bp_category"
        # add the category column to the df
        self.df = self.df.join(category_series)
        next_category_series= pd.cut(self.df.next_state, bins=10)
        # set name to category
        next_category_series.name = "next_bp_category"
        self.df = self.df.join(next_category_series)


    def __init__(self, nor_eps=0.01):
        self._init_data()
        self.bp, self.bp_category = self.__get_random_init_bp()
        self.nor_eps = nor_eps
        

    def move(self, action):
        """
        :param action: NOR dosage given by caretaker
        :return: the reward for the action
        """
        # get original_rates with distance epsilon from action
        original_rates_eps = self.df[(self.df.action >= action - self.nor_eps) & (self.df.action <= action + self.nor_eps)]
        # get the original_rates with the same bp category
        original_rates_eps_bp = original_rates_eps[original_rates_eps.bp_category.values == self.bp_category.values[0]]
        # sample a new bp from the original_rates_eps_bp
        new_bp_row = original_rates_eps_bp.sample(1)
        # update the current bp
        self.bp = new_bp_row.next_state
        self.bp_category = new_bp_row.next_bp_category

        # return the reward
        return self.__get_square_dist_from_target()
        



if __name__ == "__main__":
    patient = PatientSimulator()
    # print(patient.bp)
    print(patient.move(0.5))
    # print(patient.bp)
    # import os
    # print(os.getcwd())