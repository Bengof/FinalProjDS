import pandas as pd
import chunk_filtering


ITEM_IDS = pd.read_csv("data\icu\d_items.csv")
D_ICD_DIAGNOSIS = pd.read_csv("data\hosp\d_icd_diagnoses.csv")
DIAGNOSES_ICD = pd.read_csv("data\hosp\diagnoses_icd.csv")
PATIENTS = pd.read_csv("data\core\patients.csv")
LABITEMS = pd.read_csv("data\hosp\d_labitems.csv")

SEPSIS_PERCENTAGE = 0.9

def get_chartevents_itemids():
    contains_BP = ITEM_IDS[ITEM_IDS["label"].str.contains("BP")]
    contains_BP = contains_BP[contains_BP["category"] == "Routine Vital Signs"]["itemid"]
    Blood_Pressure_items = ITEM_IDS[ITEM_IDS["label"].str.contains("Blood Pressure")]["itemid"]
    IABP_items = ITEM_IDS[ITEM_IDS["category"] == "IABP"]["itemid"]
    MAP_items = ITEM_IDS[ITEM_IDS["label"].str.contains("MAP") | ITEM_IDS["label"].str.contains("Map")]["itemid"]
    heart_rate_items = ITEM_IDS[ITEM_IDS["label"].str.contains("Heart Rate| HR ", regex=True)]
    heart_rate_items = heart_rate_items[heart_rate_items["category"] == "Routine Vital Signs"]["itemid"]
    chartevents_itemid = pd.concat([MAP_items, IABP_items, contains_BP, Blood_Pressure_items, heart_rate_items]) 
    return chartevents_itemid


def get_labevents_itemids():
    contains_lactate = LABITEMS[LABITEMS["label"].fillna("").str.contains("Lactate")]["itemid"]
    return contains_lactate


def get_sepsis_icd_codes():
    return D_ICD_DIAGNOSIS[D_ICD_DIAGNOSIS["long_title"].str.lower().str.contains("sepsis") | D_ICD_DIAGNOSIS["long_title"].str.lower().str.contains(" septic ")][["icd_code", "long_title"]]


def get_all_sepsis_patients():
    # get all sepsis patients by codes, and then get ages from patients table
    sepsis_codes = get_sepsis_icd_codes()
    sepsis_patients = DIAGNOSES_ICD[DIAGNOSES_ICD["icd_code"].isin(sepsis_codes["icd_code"])]
    sepsis_patients = sepsis_patients.merge(sepsis_codes, left_on="icd_code", right_on="icd_code")
    sepsis_patients = sepsis_patients.merge(PATIENTS[["subject_id", "gender", "anchor_age", "dod"]], left_on="subject_id", right_on="subject_id")
    return sepsis_patients

def get_top_sepsis_patients_subject_ids():
    filtered_sepsis = pd.read_csv("filtered\\filtered_patients.csv")
    return filtered_sepsis["subject_id"]

def get_inputevents_itemids():
    medicine_items = ITEM_IDS[ITEM_IDS["label"].str.contains("phrine") | ITEM_IDS["label"].str.contains("dopamine") | ITEM_IDS["label"].str.contains("Angiotensin")
            | ITEM_IDS["label"].str.contains("Vasopressin") | ITEM_IDS["label"].str.contains("Metaraminol")]["itemid"]
    return medicine_items

def get_procedureevents_itemids():
    # beil ask for invasive mechanical ventilation - itemid=225792; renal replacement therapy / dialysis - itemid=225441
    return pd.Series([225792, 225441])

def filter_small_file(input_path, subject_ids, itemids=None):
    df = pd.read_csv(input_path)
    df = df[df["subject_id"].isin(subject_ids)]
    if type(itemids) != type(None):
        df = df[df["itemid"].isin(itemids)]
        df = df.merge(ITEM_IDS[["itemid", "label"]], left_on="itemid", right_on="itemid")
        df = df.rename(columns={"label":"itemid_label"})
    return df


def save_filtered_inputevents():
    # create filtered inputevents files (by subject id and by subject id and medicine)
    input_events = pd.read_csv("data\icu\inputevents.csv")
    input_events_subject_id = input_events[input_events["subject_id"].isin(get_top_sepsis_patients_subject_ids())]
    input_events_subject_id.to_csv("filtered\\input_events_filtered_by_subject_id.csv")
    input_events_subject_id_itemid = input_events_subject_id[input_events_subject_id["itemid"].isin(get_inputevents_itemids())]
    input_events_subject_id_itemid = input_events_subject_id_itemid.merge(ITEM_IDS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    input_events_subject_id_itemid = input_events_subject_id_itemid.rename(columns={"label":"itemid_label"})
    input_events_subject_id_itemid.to_csv("filtered\\input_events_filtered_by_subject_id_and_medicine.csv")

def save_filtered_chartevents():
    filtered_chartevents = chunk_filtering.filter_big_file("data\icu\chartevents.csv", get_top_sepsis_patients_subject_ids(), get_chartevents_itemids())
    filtered_chartevents = filtered_chartevents.merge(ITEM_IDS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    filtered_chartevents = filtered_chartevents.rename(columns={"label":"itemid_label"})
    filtered_chartevents.to_csv("filtered\\filtered_chartevents.csv")

def save_filtered_icustays():
    filtered_icustays = chunk_filtering.filter_big_file("data\icu\icustays.csv", get_top_sepsis_patients_subject_ids())
    filtered_icustays.to_csv("filtered\\filtered_icustays.csv")

def save_filtered_procedureevents():
    filtered_procedureevents = filter_small_file("data\\icu\\procedureevents.csv", get_top_sepsis_patients_subject_ids(), get_procedureevents_itemids())
    filtered_procedureevents.to_csv("filtered\\filtered_procedureevents.csv")

def save_filtered_transfers():
    filtered_procedureevents = filter_small_file("data\\core\\transfers.csv", get_top_sepsis_patients_subject_ids())
    filtered_procedureevents.to_csv("filtered\\filtered_transfers.csv")

def save_filtered_labevents():
    filtered_labevents = chunk_filtering.filter_big_file("data\hosp\labevents.csv", get_top_sepsis_patients_subject_ids(), get_labevents_itemids())
    filtered_labevents = filtered_labevents.merge(LABITEMS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    filtered_labevents = filtered_labevents.rename(columns={"label":"itemid_label"})
    filtered_labevents.to_csv("filtered\\filtered_labevents.csv")

def save_filtered_patients(percents=SEPSIS_PERCENTAGE):
    sepsis_patients = get_all_sepsis_patients()
    # different_sepsis_amounts = sepsis_patients.groupby(by="long_title").agg({"subject_id": "count"}).sort_values(by="subject_id", ascending=False)
    # different_sepsis_amounts_normalized = different_sepsis_amounts.cumsum()/different_sepsis_amounts.sum()
    # different_sepsis_amounts_normalized = different_sepsis_amounts_normalized.reset_index()
    # top_titles = different_sepsis_amounts_normalized[different_sepsis_amounts_normalized["subject_id"] <= percents]["long_title"]
    # filtered_sepsis = sepsis_patients[sepsis_patients["long_title"].isin(top_titles)]
    sepsis_patients.to_csv("filtered\\filtered_patients.csv")