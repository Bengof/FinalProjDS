import imp
import filter_data
import states_creator
import pandas as pd
from bp_for_dose import get_relevant_doses_with_bp


def run_pipeline():
    input_events = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    icus_events = pd.read_csv("filtered\\filtered_icustays.csv")
    filtered_inputs_df = filter_data.filter_short_stays_and_different_unit(input_events, icus_events)
    inputevents_with_bp = get_relevant_doses_with_bp(filtered_inputs_df) #TODO: change
    return inputevents_with_bp[inputevents_with_bp.itemid_label == "Norepinephrine"] # keep Norepinephrine only
    

