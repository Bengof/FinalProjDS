import pandas as pd

def get_events_beofore_dose(event_time, interval, stay_id, table, time_field, is_procedure=False):
    if is_procedure: 
        table[time_field[0]] = pd.to_datetime(table[time_field[0]])
        table[time_field[1]] = pd.to_datetime(table[time_field[1]])
    else:    
        table[time_field] = pd.to_datetime(table[time_field])
    event_time = pd.Timestamp(event_time)
    interval = pd.Timedelta(value=interval, unit="hours")
    events = table[table["stay_id"] == stay_id]
    if is_procedure: # labevents, chartsevents
        start, end = time_field[0], time_field[1]
        events = events[((events[end] >= event_time - interval) & (events[end] <= event_time)) | # finishes in the interval
                        ((events[end] >= event_time) & (events[start] <= event_time))] # starts before the event and ends after the event
    else: # procedure
        events = events[(events[time_field] >= event_time - interval) & (events[time_field] <= event_time)]
    return events
