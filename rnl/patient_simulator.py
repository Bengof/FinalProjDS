import pandas as pd
import numpy as np

# DATA_PATH = "../processed/full_pipeline_ok_filtered.csv" #TODO: have a file with dose=0
# DATA_PATH = "rnl\dummy_data\dummy_data.csv"
DATA_PATH = "RNLData/bps_with_doses_fixed.csv"
TARGET_BP = 65
# BINS = pd.IntervalIndex.from_tuples([(40, 60), (60, 80), (80, 100), (100, 120), (120, 140), (140, 160), (160, 180), (180, 200)])
from rnl_consts import *

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
    def __get_random_init_bp(self):
        # get random bp from samples who are marked first
        first_bp_per_stay = self.df[self.df["first"]].sample(1)
        # print(first_bp_per_stay.to_())
        # return the bp
        return first_bp_per_stay["cur_bp"].values[0], first_bp_per_stay["bp_category"].values[0]
    
    def __get_square_dist_from_target(self):
        return - ((self.bp - TARGET_BP) ** 2)

    # def _init_data(self):
    #     df = pd.read_csv(DATA_PATH)
    #     df = df[(df.cur_bp > 0) & (df.cur_bp < 200)] #TODO: do it in the preprocessing
    #     df = df[(df.next_bp > 0) & (df.next_bp < 200)] #TODO: do it in the preprocessing
    #     # replace field dose np.nan with 0
    #     df["dose"] = df["dose"].fillna(0)
    #     self.df = add_first_and_last_indicators(df)
    #     # get bins for dose and bp
    #     category_series= pd.cut(self.df.cur_bp, bins=BINS)
    #     # set name to category
    #     category_series.name = "bp_category"
    #     # add the category column to the df
    #     self.df = self.df.join(category_series)
    #     next_category_series= pd.cut(self.df.next_bp, bins=BINS)
    #     # set name to category
    #     next_category_series.name = "next_bp_category"
    #     self.df = self.df.join(next_category_series)


    def __init__(self, nor_eps=0.01):
        # self._init_data()
        self.df = pd.read_csv(DATA_PATH)
        self.bp, self.bp_category = self.__get_random_init_bp()
        # first_bp_per_stay = self.df.iloc[0]
        # self.bp, self.bp_category = first_bp_per_stay.cur_bp, first_bp_per_stay.bp_category
        self.nor_eps = nor_eps
        

    def get_random_state(self, cur_bp):
        pass


    def move(self, dose):
        """
        :param dose: NOR dosage given by caretaker
        :return: the reward for the dose
        """
        # get original_rates with distance epsilon from dose
        original_rates_eps = self.df[(self.df.dose >= dose - self.nor_eps) & (self.df.dose <= dose + self.nor_eps)]
        # get the original_rates with the same bp category
        original_rates_eps_bp = original_rates_eps[original_rates_eps.bp_category == self.bp_category]

        #TODO: replace with soft thresholding
        new_bp_row = original_rates_eps_bp.sample(1) if len(original_rates_eps_bp) > 0 else self.df.sample(1)
        # update the current bp
        self.bp = new_bp_row.next_bp.values[0]
        self.bp_category = new_bp_row.next_bp_category.values[0]
        self.is_game_over = new_bp_row["last"].values[0]
        if self.bp <= 0:
            self.bp = 0
            self.is_game_over = True
            self.bp_category = BINS[0]

        # return the new state and reward
        return self.bp_category, self.__get_square_dist_from_target()
        
    def game_over(self):
        return self.is_game_over


if __name__ == "__main__":
    patient = PatientSimulator(nor_eps=0.05)
    # print(patient.bp)
    print(patient.move(1))
    # print(patient.bp)
    # import os
    # print(os.getcwd())
    # df = pd.read_csv(DATA_PATH)
    # df = add_first_and_last_indicators(df)
    # sort df by stay_id and cur_bp_time
    # df = df.sort_values(["stay_id", "cur_bp_time"])
    # print(df[df["stay_id"] == 12])