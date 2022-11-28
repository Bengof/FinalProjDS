import numpy as np
import filter_data
import pandas as pd
from bp_for_dose import get_relevant_doses_with_bp
import filter_data


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


if '__main__' == __name__:
    inputevents_states_ok, inputevents_states_full = run_pipeline(create_filtered_files_flag=True)
    inputevents_states_ok.to_csv("processed\\full_pipeline_ok_filtered.csv")
    inputevents_states_full.to_csv("processed\\full_pipeline_full.csv")

