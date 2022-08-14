import inputs_states_filters
import pandas as pd
import numpy as np
from preceding_events import get_events_beofore_dose, get_prev_dose
from states_creator import create_states
import consts
from tqdm import tqdm 

def get_nearest_bp(dose_row, chartevent):
    interval = dose_row["starttime"] - dose_row["prev_starttime"]
    # in case that there is no previous dose event, set the interval to the default
    if pd.isna(interval):
        interval = pd.Timedelta(consts.HOURS_BEFORE_DOSE, unit="hour")
    events = get_events_beofore_dose(dose_row["starttime"], interval, dose_row["stay_id"], chartevent, "charttime")
    # filter out events which are not BP events
    bp_events = events[events["itemid"].isin(consts.BP)]
    # select the first closest event, and leave only its time and value:
    bp_event = bp_events.sort_values(by="charttime", ascending=False).head(1)[["charttime","value"]].squeeze()
    # return nan in case that no bp exist in the interval
    if bp_events.size == 0:
        return [np.nan, np.nan]
    return bp_event.to_list()

def get_relevant_doses_with_bp(inputevents, chartevent):
    inputevents_states = create_states(inputevents)
    # keep only events with no overlaps and other problems:
    inputevents_states_ok = inputevents_states[inputevents_states["State"] == consts.State.OK].copy()
    inputevents_states_ok = inputevents_states_ok[["stay_id","starttime","endtime", "rate", "statusdescription", "originalrate", "itemid_label", "State"]].sort_values(by=["stay_id","starttime"])
    # add to each row the prev_starttime:
    inputevents_states_ok = get_prev_dose(inputevents_states_ok)
    # select to each dose what is the closest BP events in the interval
    tqdm.pandas()
    inputevents_states_ok[["bp_time","bp_val"]] = inputevents_states_ok.progress_apply(lambda row: get_nearest_bp(row, chartevent), axis=1, result_type="expand")
    return inputevents_states, inputevents_states_ok