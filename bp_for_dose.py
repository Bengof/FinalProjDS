import inputs_states_filters
import pandas as pd
import numpy as np
from preceding_events import get_events_beofore_dose, add_prev_decision
import consts

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

def get_relevant_doses_with_bp(chartevent):
    # get input events with states for each row if it is relevant and the reason for irrelevant:
    inputevents_states = inputs_states_filters.get_inputs_with_states()
    # keep only events with no overlaps and other problems:
    inputevents_states = inputevents_states[inputevents_states["state"] == inputs_states_filters.State.OK]
    inputevents_states = inputevents_states[["stay_id","starttime","endtime", "rate", "statusdescription", "originalrate", "itemid_label", "state"]].sort_values(by=["stay_id","starttime"])
    # add to each row the prev_starttime:
    inputevents_states = add_prev_decision(inputevents_states)
    # select to each dose what is the closest BP events in the interval
    inputevents_states[["bp_time","bp_val"]] = inputevents_states.apply(lambda row: get_nearest_bp(row, chartevent), axis=1, result_type="expand")
    return inputevents_states