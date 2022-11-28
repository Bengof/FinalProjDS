import imp
import pandas as pd
from consts import *
import os
from tqdm import tqdm
from enum import Enum

def check_if_change_in_rate_smaller_than_epsilon(df_inputs, stay_id, epsilon, status_description):
        input_for_patient = df_inputs[(df_inputs["stay_id"] == stay_id) & (df_inputs["statusdescription"] == status_description) &( df_inputs["itemid_label"] == "Norepinephrine")][["stay_id", "starttime", "endtime", "statusdescription", "originalrate", "rate", "itemid_label"]].sort_values(by="starttime")
        if input_for_patient.shape[0] == 0:
                return False
        previous_rate = input_for_patient.iloc[0]["originalrate"]
        previous_endtime = input_for_patient.iloc[0]["endtime"]
        for row in input_for_patient[1:].itertuples():
                if abs(row.originalrate - previous_rate) < epsilon and previous_endtime == row.starttime:
                        # print("stay_id: {}, status_description: {}, rate: {}, originalrate: {}, starttime: {}, endtime: {}".format(stay_id, status_description, row.rate, row.originalrate, row.starttime, row.endtime))
                        return True
                previous_rate = row.originalrate
                previous_endtime = row.endtime
        return False

def get_inputs_with_states(epsilon=0.001):
    """
    Returns a tuple of time serieses: ChangeDoes, Paused, Stopped
    """
    df_overlaps = pd.read_csv('..\\filtered\\overlaps_df.csv')
    overlapped_stay_ids = df_overlaps[df_overlaps["overlaps"] > 0]["stay_id"].unique()
    not_overlapped_stay_ids = df_overlaps[df_overlaps["overlaps"] == 0]["stay_id"].unique()
    df_inputs = pd.read_csv("..\\filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    
    stay_ids_with_change_in_rate_smaller_than_epsilon = []
    for stay_id in tqdm(list(not_overlapped_stay_ids)):
        if check_if_change_in_rate_smaller_than_epsilon(df_inputs, stay_id, epsilon, "ChangeDose/Rate"):
            stay_ids_with_change_in_rate_smaller_than_epsilon.append(stay_id)
    df_inputs["state"] = State.OK
    df_inputs = df_inputs[df_inputs["itemid_label"] == "Norepinephrine"]
    df_inputs.loc[df_inputs["stay_id"].isin(stay_ids_with_change_in_rate_smaller_than_epsilon), "state"] = State.LESS_THAN_EPSILON
    df_inputs.loc[df_inputs["stay_id"].isin(overlapped_stay_ids), "state"] = State.OVERLAPPED_WITH_DIFFERENT_MED
    return df_inputs
    
    
 
