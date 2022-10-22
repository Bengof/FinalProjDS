import pandas as pd
import numpy as np
import random
import datetime

# new df with 3 cols
df = pd.DataFrame(columns=["stay_id","cur_state","bp_time", "action", "next_state"])
# add rows
for i in range(1000):
    #create a random time
    time = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(0, 1000))
    df.loc[i] = [np.random.randint(0, 15), np.random.randint(40, 200), time ,random.uniform(0, 1), np.random.randint(40, 200)]
    # df = df.append({"cur_state": i, "action": i+1, "next_state": i+2}, ignore_index=True)
# save to csv
df.to_csv("rnl\dummy_data\dummy_data.csv", index=False)