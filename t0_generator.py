import pandas as pd

def get_filtered_stay_ids():
    df = pd.read_csv('filtered\\overlaps_df.csv')
    return df[df["overlaps"] == 0][["stay_id"]]

def get_t0():
    """
    Returns a tuple of time serieses: ChangeDoes, Paused, Stopped
    """
    df_inputs = pd.read_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")
    no_overlap_stay_ids = get_filtered_stay_ids()
    df_inputs = df_inputs[df_inputs["stay_id"].isin(no_overlap_stay_ids["stay_id"])]
    df_inputs = df_inputs[df_inputs["itemid_label"] == "Norepinephrine"]
    df_inputs_changed = df_inputs[df_inputs["statusdescription"] == "ChangeDose/Rate"][["stay_id", "subject_id", "starttime", "endtime"]].sort_values(by="starttime")
    df_inputs_paused = df_inputs[df_inputs["statusdescription"] == "Paused"][["stay_id", "subject_id", "starttime", "endtime"]].sort_values(by="starttime")
    df_inputs_stopped = df_inputs[df_inputs["statusdescription"] == "Stopped"][["stay_id", "subject_id", "starttime", "endtime"]].sort_values(by="starttime")
    return df_inputs_changed, df_inputs_paused, df_inputs_stopped
 