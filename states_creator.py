from tqdm import tqdm
import pandas as pd
import numpy as np
import consts

def mark_ne_events_that_overlap(df):
    """
    Marks events that overlap with other ne and other meds
    """
    nor_overlap_indicies = []
    med_overlap_indicies = []
    for stay_id in tqdm(df["stay_id"].unique()):
        patient_noreadrenaline = df[(df["stay_id"] == stay_id) & (df["itemid_label"] == "Norepinephrine")][["input_index", "starttime", "endtime", "statusdescription", "originalrate", "itemid_label"]].sort_values(by="starttime")
        patient_full_inputs = df[(df["stay_id"] == stay_id) ][["input_index", "starttime", "endtime", "statusdescription", "originalrate", "itemid_label"]].sort_values(by="starttime")
        for noreadrenaline_event in patient_noreadrenaline.itertuples():
            for med_event in patient_full_inputs.itertuples():
                if med_event.starttime < noreadrenaline_event.starttime and med_event.endtime > noreadrenaline_event.starttime\
                    and med_event.input_index != noreadrenaline_event.input_index:
                    if med_event.itemid_label == "Norepinephrine": #TODO: look at statusdescription here 
                        nor_overlap_indicies.append(noreadrenaline_event.input_index)
                    else:
                        med_overlap_indicies.append(noreadrenaline_event.input_index)
    df.loc[df["input_index"].isin(nor_overlap_indicies), "State"] = consts.State.OVERLAPPED_WITH_ANOTHER_NE
    df.loc[df["input_index"].isin(med_overlap_indicies), "State"] = consts.State.OVERLAPPED_WITH_DIFFERENT_MED
    return df


def create_states(inputs_df):
    inputs_df["State"] = np.nan

    return mark_ne_events_that_overlap(inputs_df)

    

if '__main__' == __name__:
    inputs_df = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    inputs_df = inputs_df.rename(columns={"Unnamed: 0": "input_index"})
    icus_df = pd.read_csv("filtered\\filtered_icustays.csv")
    # filtered_inputs_df = filter_data.filter_short_stays_and_different_unit(inputs_df, icus_df)
    # select random 1000 stay_ids
    stay_ids = icus_df["stay_id"].sample(n=500)
    filtered_inputs_df = inputs_df[inputs_df["stay_id"].isin(stay_ids)].copy()
    inputs_with_states_df = create_states(filtered_inputs_df)
    inputs_with_states_df.to_csv("tmp\\inputs_with_states.csv")