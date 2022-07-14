from tkinter import N
import pandas as pd
import numpy as np
import consts
import preceding_events

WINDOWING_CONFIG={
  "hr": {
    "time_field":"charttime",
    "table": None,
    "itemid": consts.HR
  },
  "bp": {
    "time_field":"charttime",
    "table": None,
    "itemid": consts.BP
  },
  "lactate" :{
    "time_field":"charttime",
    "table":None,
    "itemid": consts.LABEVENTS_CODES
  },
  "procedure":{
    "time_field":("starttime","endtime"),
    "table": None,
    "itemid": consts.PROCEDURE_CODES
  }
}

def update_config(chatevents, labevents, procedureevents):
    WINDOWING_CONFIG["procedure"]["table"] = procedureevents
    WINDOWING_CONFIG["bp"]["table"] = chatevents
    WINDOWING_CONFIG["lactate"]["table"] = labevents

def window_statistics(events, type):
    if not events.empty:
        if type != "procedure":
            events_lst = events[["charttime", "value"]].apply(lambda row: (row["charttime"], row["value"]), axis=1).to_list()
        else:
            events_lst = events[["starttime", "endtime", "value"]].apply(lambda row: (row["starttime"], row["endtime"], row["value"]), axis=1).to_list()
    else:
        events_lst = np.nan
    return [events["value"].max(), 
            events["value"].min(), 
            events["value"].std(),
            events["value"].mean(),
            events["value"].count(),
            str(events_lst)]


def windowing_for_row(input_events_row, interval, type):
  stay_id = input_events_row["stay_id"]
  event_time = input_events_row["starttime"]
  config = WINDOWING_CONFIG[type]
  pe_chartevents = preceding_events.get_events_beofore_dose(event_time, interval, stay_id, config["table"], config["time_field"], type=="procedure")
  events = pe_chartevents[pe_chartevents["itemid"].isin(config["itemid"])]  
  return window_statistics(events, type)


def filter_short_stays_and_different_unit(inputevents, icustays_filtered):
    icustays_filtered = icustays_filtered[icustays_filtered["first_careunit"] == icustays_filtered["last_careunit"]]
    icustays_filtered = icustays_filtered[icustays_filtered["los"] >= consts.MINIMAL_LOS]
    inputevents = inputevents.merge(icustays_filtered[["stay_id", "first_careunit"]], left_on="stay_id", right_on="stay_id")
    return inputevents

def add_window_statistics(input_events, event_type):
    statistics = input_events.apply(lambda row:windowing_for_row(row, consts.HOURS_BEFORE_DOSE, event_type), axis=1, result_type="expand")
    statistics = statistics.rename(columns={
                                        0:f"{event_type}_max",
                                        1:f"{event_type}_min",
                                        2:f"{event_type}_std",
                                        3:f"{event_type}_mean",
                                        4:f"{event_type}_count",
                                        5:f"{event_type}_events_at_interval"})
    return pd.concat([input_events, statistics], axis=1)    

def add_all_statistics(inputevents):
    inputevents = inputevents[["subject_id","hadm_id","stay_id","starttime","endtime","storetime","itemid","itemid_label","amount","amountuom","rate","rateuom","statusdescription","patientweight", "first_careunit"]]
    for info_type in ["bp", "hr", "lactate", "procedure"]:
        inputevents = add_window_statistics(inputevents, info_type)
    return inputevents

def create_combined_df(inputevent, icustays, chartevents, labevents, procedureevents):
    update_config(chartevents, labevents, procedureevents)
    inputevents_filtered_by_los = filter_short_stays_and_different_unit(inputevent, icustays)
    combined_df = add_all_statistics(inputevents_filtered_by_los)
    combined_df.to_csv("combined/combined_df.csv")