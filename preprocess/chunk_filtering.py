import os
import pandas as pd
import shutil

chucnksize = 10 ** 7


def filter_chunks(input_path, output_path, subject_ids=None, item_ids=None, subject_id_col_name="subject_id",
                  itemid_col_name="itemid"):
    with pd.read_csv(input_path, chunksize=chucnksize) as reader:
        counter = 0
        for chunk in reader:
            print(chunk.shape)
            # filter by subject_ids
            if type(subject_ids) != type(None):
                chunk = chunk[chunk[subject_id_col_name].isin(subject_ids)]
            # filter by item_ids
            if type(item_ids) != type(None):
                chunk = chunk[chunk[itemid_col_name].isin(item_ids)]
            # create new folder
            chunk.to_csv(output_path + "\\" + str(counter) + ".csv")
            print(f"chunk number:{counter}, rows amount:{chunk.shape}")
            counter += 1


def combine_filtered_chunks(input_path):
    # combine all charteventsfrom os import listdir
    df = pd.DataFrame({})
    for file in os.listdir(input_path):
        df_tmp = pd.read_csv(input_path + '\\' + file)
        df = pd.concat([df, df_tmp])
    return df


def filter_big_file(input_path, subject_ids=None, item_ids=None, subject_id_col_name="subject_id",
                    itemid_col_name="itemid"):
    tmp_path = "tmp"
    if not os.path.exists(tmp_path):
        print("create tmp folder for chunks results")
        os.makedirs(tmp_path)
    else:
        shutil.rmtree(tmp_path)
        print("delete previous tmp folder")
        os.makedirs(tmp_path)
        print("create new folder after deleting old")
    print("start chunk by chunk")
    filter_chunks(input_path, tmp_path, subject_ids, item_ids, subject_id_col_name=subject_id_col_name,
                  itemid_col_name=itemid_col_name)
    print("combine chunks")
    combined = combine_filtered_chunks(tmp_path)
    if os.path.exists(tmp_path):
        print("delete tmp folder")
        shutil.rmtree(tmp_path)
    return combined
