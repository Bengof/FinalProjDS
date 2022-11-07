import numpy as np
import filter_data
import pandas as pd
from bp_for_dose import get_relevant_doses_with_bp
import filter_data
from tqdm import tqdm
from rnl.rnl_consts import *

def create_filtered_files():
    """
    Creates filtered files for the pipeline. Default path is "filtered".
    """
    filter_data.save_filtered_patients()
    filter_data.save_filtered_chartevents()
    filter_data.save_filtered_inputevents()
    filter_data.save_filtered_icustays()
    # filter_data.save_filtered_procedureevents()
    # filter_data.save_filtered_labevents()
    # filter_data.save_filtered_transfers()


def run_pipeline(count_samples_stay_ids=None, create_filtered_files_flag=False):
    if create_filtered_files_flag:
        create_filtered_files()
    input_events = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    print("Read input events")
    chart_events = pd.read_csv("filtered\\filtered_chartevents.csv")
    print("Read chart events")
    icus_events = pd.read_csv("filtered\\filtered_icustays.csv")
    print("Read icustays")


    if count_samples_stay_ids is not None:
        unique_stay_ids = input_events["stay_id"].unique()
        np.random.seed(0)
        stay_ids = np.random.choice(unique_stay_ids, count_samples_stay_ids, replace=False)
        input_events = input_events[input_events["stay_id"].isin(stay_ids)]
        chart_events = chart_events[chart_events["stay_id"].isin(stay_ids)]
        icus_events = icus_events[icus_events["stay_id"].isin(stay_ids)]

    filtered_inputs_df = filter_data.filter_short_stays_and_different_unit(input_events, icus_events)
    inputevents_states_full, inputevents_states_ok = get_relevant_doses_with_bp(filtered_inputs_df, chart_events)
    return inputevents_states_ok[inputevents_states_ok.itemid_label == "Norepinephrine"], inputevents_states_full


def _read_bp_rnl(chartevents_path):
    bps = pd.read_csv(chartevents_path)
    # keep only BP event from the specific type we need
    bps = bps[bps.itemid.isin([225312, 220052, 220181])]
    bps = bps.rename(columns={"value": "cur_bp", "charttime":"cur_bp_time"})
    bps = bps.drop(columns=["Unnamed: 0", "Unnamed: 0.1", "valuenum", "warning", "itemid_label", "storetime", "valueuom"])
    # remove bps > 200 and < 0
    bps = bps[(bps.cur_bp <= 200) & (bps.cur_bp >= 0)]
    return bps

def doses_per_stay_id(stay_id, bps, doses):
    bps_stay_id_subset = bps[bps.stay_id == stay_id]
    doses_stay_id_subset = doses[doses.stay_id == stay_id]
    bps_stay_id_subset = bps_stay_id_subset.sort_values(by="cur_bp_time")
    bps_stay_id_subset["next_bp"] = bps_stay_id_subset["cur_bp"].shift(-1)
    bps_stay_id_subset["next_bp_time"] = bps_stay_id_subset["cur_bp_time"].shift(-1)
    bps_stay_id_subset["dose"] = bps_stay_id_subset.apply(lambda row: match_dose(row, doses_stay_id_subset), axis=1)

    return bps_stay_id_subset
    
def match_dose(bp_row, doses):
        relevant_doses = doses[(bp_row["cur_bp_time"] <= doses["starttime"]) & 
                                    (bp_row["next_bp_time"] > doses["starttime"])]
        dose = relevant_doses.head(1)[["originalrate", "starttime", "endtime"]]
        if dose.size == 3:
            return dose.values[0][0]
        else:
            return None
            


def add_first_and_last_indicators(df):
    # add first and last indicators
    # sort by stay_id and cur_bp_time
    df = df.sort_values(["stay_id", "cur_bp_time"], ascending=False)
    df["last"] = df.groupby("stay_id").cumcount() == 0
    df = df.sort_values(["stay_id", "cur_bp_time"], ascending=True)
    df["first"] = df.groupby("stay_id").cumcount() == 0
    return df

def add_bp_catgeories(df):
    # get bins for dose and bp
    category_series= pd.cut(df.cur_bp, bins=BINS).astype(str)
    # set name to category
    category_series.name = "bp_category"
    # add the category column to the df
    df = df.join(category_series)
    next_category_series= pd.cut(df.next_bp, bins=BINS).astype(str)
    # set name to category
    next_category_series.name = "next_bp_category"
    df = df.join(next_category_series)
    return df

def generate_rnl_bp_events(chartevents_path, decisions_after_pipeline_path):
    # read the BP events file
    bps = _read_bp_rnl(chartevents_path)
    # read the inputevents file after our preprocess
    decisions_after_pipeline = pd.read_csv(decisions_after_pipeline_path)
    
    stay_ids = decisions_after_pipeline.stay_id.unique() 
    bps_and_dose = None
    for stay_id in tqdm(stay_ids):
        bps_and_dose_per_stay = doses_per_stay_id(stay_id, bps , decisions_after_pipeline)
        if bps_and_dose is not None:
            bps_and_dose = pd.concat([bps_and_dose, bps_and_dose_per_stay],axis=0)
        else:
            bps_and_dose = bps_and_dose_per_stay

    bps_and_dose["dose"] = bps_and_dose["dose"].fillna(0)
    bps_and_dose = add_first_and_last_indicators(bps_and_dose)
    bps_and_dose = add_bp_catgeories(bps_and_dose)

    return bps_and_dose




if '__main__' == __name__:
    # inputevents_states_ok, inputevents_states_full = run_pipeline(create_filtered_files_flag=True)
    # inputevents_states_ok.to_csv("processed\\full_pipeline_ok_filtered.csv")
    # inputevents_states_full.to_csv("processed\\full_pipeline_full.csv")
    bp_rnl = generate_rnl_bp_events("filtered\\filtered_chartevents.csv", "processed\\full_pipeline_ok_filtered.csv")
    bp_rnl.to_csv("RNLData\\bps_with_doses_sanity.csv")

