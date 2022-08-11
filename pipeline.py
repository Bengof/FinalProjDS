import filter_data
import states_creator
import pandas as pd


def run_pipeline():
    input_events = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    icus_events = pd.read_csv("filtered\\filtered_icustays.csv")
    filtered_inputs_df = filter_data.filter_short_stays_and_different_unit(input_events, icus_events)
    inputs_with_states_df = states_creator.create_states(filtered_inputs_df)
    return merge_inputs_with_bp_events() #TODO: change

