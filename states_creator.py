from tqdm import tqdm
import pandas as pd
import numpy as np
import consts

NOR_OVERLAP_STATUS_DESC_TO_STATE = {
    "FinishedRunning": consts.State.OVERLAPPED_WITH_ANOTHER_NE_FINISHED,
    "Paused": consts.State.OVERLAPPED_WITH_ANOTHER_NE_PAUSED,
    "Stopped": consts.State.OVERLAPPED_WITH_ANOTHER_NE_STOPPED,
    "ChangeDose/Rate": consts.State.OVERLAPPED_WITH_ANOTHER_NE_CHANGED_DOSE,
}

NOR_EPS_STATUS_DESC_TO_STATE = {
    "FinishedRunning": consts.State.LESS_THAN_EPSILON_FINISHED,
    "Paused": consts.State.LESS_THAN_EPSILON_PAUSED,
    "Stopped": consts.State.LESS_THAN_EPSILON_STOPPED,
    "ChangeDose/Rate": consts.State.LESS_THAN_EPSILON_CHANGED_DOSE,
}

def mark_ne_events_that_overlap(df):
    """
    Marks events that overlap with other ne and other meds
    """
    for stay_id in tqdm(df["stay_id"].unique()):
        patient_noreadrenaline = df[(df["stay_id"] == stay_id) & (df["itemid_label"] == "Norepinephrine")][["input_index", "starttime", "endtime", "statusdescription", "originalrate", "itemid_label", "State"]].sort_values(by="starttime")
        patient_full_inputs = df[(df["stay_id"] == stay_id) ][["input_index", "starttime", "endtime", "statusdescription", "originalrate", "itemid_label", "State"]].sort_values(by="starttime")
        for noreadrenaline_event in patient_noreadrenaline.itertuples():
            for med_event in patient_full_inputs.itertuples():
                if med_event.starttime <= noreadrenaline_event.starttime and med_event.endtime > noreadrenaline_event.starttime\
                    and med_event.input_index != noreadrenaline_event.input_index:
                    if med_event.itemid_label == "Norepinephrine":
                        df.loc[df["input_index"] == noreadrenaline_event.input_index, "State"] = NOR_OVERLAP_STATUS_DESC_TO_STATE[med_event.statusdescription]
                    else:
                        df.loc[df["input_index"] == noreadrenaline_event.input_index, "State"] = consts.State.OVERLAPPED_WITH_DIFFERENT_MED
    return df


def mark_epsilon(df_inputs, epsilon):
    for stay_id in tqdm(df_inputs["stay_id"].unique()):
        input_for_patient = df_inputs[(df_inputs["stay_id"] == stay_id) & (df_inputs["itemid_label"] == "Norepinephrine")][["stay_id", "starttime", "endtime", "statusdescription", "originalrate", "input_index", "itemid_label", "State"]].sort_values(by="starttime")
        if len(input_for_patient) == 0:
            continue
        previous_rate = input_for_patient.iloc[0]["originalrate"]
        previous_endtime = input_for_patient.iloc[0]["endtime"]
        previous_status = input_for_patient.iloc[0]["statusdescription"]
        for row in input_for_patient[1:].itertuples():
                if abs(row.originalrate - previous_rate) < epsilon and previous_endtime == row.starttime:
                        df_inputs.loc[df_inputs["input_index"] == row.input_index, "State"] = NOR_EPS_STATUS_DESC_TO_STATE[previous_status]
                previous_rate = row.originalrate
                previous_endtime = row.endtime
                previous_status = row.statusdescription
    return df_inputs

def create_states(inputs_df):
    inputs_df["State"] = np.nan    
    df =  mark_ne_events_that_overlap(inputs_df)
    return mark_epsilon(df, 0.001)


if '__main__' == __name__:
    inputs_df = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    inputs_df = inputs_df.rename(columns={"Unnamed: 0": "input_index"})
    icus_df = pd.read_csv("filtered\\filtered_icustays.csv")
    # filtered_inputs_df = filter_data.filter_short_stays_and_different_unit(inputs_df, icus_df)
    # select random 1000 stay_ids
    np.random.seed(0)
    stay_ids = icus_df["stay_id"].sample(n=1000)
    filtered_inputs_df = inputs_df[inputs_df["stay_id"].isin(stay_ids)].copy()
    inputs_with_states_df = create_states(filtered_inputs_df)
    inputs_with_states_df.to_csv("tmp\\inputs_with_states.csv")