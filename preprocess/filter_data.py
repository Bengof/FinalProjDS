from asyncio import constants
import pandas as pd
import chunk_filtering
import consts
import importlib
importlib.reload(consts)

ITEM_IDS = pd.read_csv("../data/icu/d_items.csv")
D_ICD_DIAGNOSIS = pd.read_csv("../data/hosp/d_icd_diagnoses.csv")
DIAGNOSES_ICD = pd.read_csv("../data/hosp/diagnoses_icd.csv")
PATIENTS = pd.read_csv("../data/core/patients.csv")
LABITEMS = pd.read_csv("../data/hosp/d_labitems.csv")


def get_chartevents_itemids():
    return pd.Series(list(consts.CHARTEVENTS_CODES))


def get_labevents_itemids():
    return pd.Series(list(consts.LABEVENTS_CODES))


def get_sepsis_icd_codes():
    return pd.Series(consts.ICD_CODES)


def get_inputevents_itemids():
    return pd.Series(list(consts.INPUTEVENTS_CODES))


def get_procedureevents_itemids():
    return pd.Series(list(consts.PROCEDURE_CODES))
    

def get_sepsis_subject_ids():
    filtered_sepsis = pd.read_csv("../filtered/filtered_patients.csv")
    return filtered_sepsis["subject_id"]


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
    input_events = pd.read_csv("../data/icu/inputevents.csv")
    input_events_subject_id = input_events[input_events["subject_id"].isin(get_sepsis_subject_ids())]
    input_events_subject_id_itemid = input_events_subject_id[input_events_subject_id["itemid"].isin(get_inputevents_itemids())]
    input_events_subject_id_itemid = input_events_subject_id_itemid.merge(ITEM_IDS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    input_events_subject_id_itemid = input_events_subject_id_itemid.rename(columns={"label":"itemid_label"})
    input_events_subject_id_itemid.to_csv("filtered\\filtered_input_events.csv")

def save_filtered_chartevents():
    filtered_chartevents = chunk_filtering.filter_big_file("../data/icu/chartevents.csv", get_sepsis_subject_ids(), get_chartevents_itemids())
    filtered_chartevents = filtered_chartevents.merge(ITEM_IDS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    filtered_chartevents = filtered_chartevents.rename(columns={"label":"itemid_label"})
    filtered_chartevents.to_csv("filtered\\filtered_chartevents.csv")

def save_filtered_icustays():
    filtered_icustays = chunk_filtering.filter_big_file("../data/icu/icustays.csv", get_sepsis_subject_ids())
    filtered_icustays.to_csv("filtered\\filtered_icustays.csv")

def save_filtered_procedureevents():
    filtered_procedureevents = filter_small_file("../data/icu/procedureevents.csv", get_sepsis_subject_ids(), get_procedureevents_itemids())
    filtered_procedureevents.to_csv("filtered\\filtered_procedureevents.csv")

def save_filtered_transfers():
    filtered_procedureevents = filter_small_file("../data/core/transfers.csv", get_sepsis_subject_ids())
    filtered_procedureevents.to_csv("filtered\\filtered_transfers.csv")

def save_filtered_labevents():
    filtered_labevents = chunk_filtering.filter_big_file("../data/hosp/labevents.csv", get_sepsis_subject_ids(), get_labevents_itemids())
    filtered_labevents = filtered_labevents.merge(LABITEMS[["itemid", "label"]], left_on="itemid", right_on="itemid")
    filtered_labevents = filtered_labevents.rename(columns={"label":"itemid_label"})
    filtered_labevents = filtered_labevents.drop(filtered_labevents[filtered_labevents["value"] == "-"].index)
    filtered_labevents["value"] = filtered_labevents["value"].astype(float)
    filtered_labevents.to_csv("filtered\\filtered_labevents.csv")

def save_filtered_patients():
    sepsis_codes = get_sepsis_icd_codes()
    patients_subject_ids = DIAGNOSES_ICD[DIAGNOSES_ICD["icd_code"].isin(sepsis_codes)][["subject_id", "icd_code", "icd_version"]]
    sepsis_patients = PATIENTS.merge(patients_subject_ids, left_on="subject_id", right_on="subject_id")
    sepsis_patients = sepsis_patients[(sepsis_patients["anchor_age"] >= consts.MINIMAL_AGE) & (sepsis_patients["anchor_age"] <= consts.MAXIMAL_AGE)]
    sepsis_patients.to_csv("filtered\\filtered_patients.csv")

def filter_short_stays_and_different_unit(inputevents, icustays_filtered):
    icustays_filtered = icustays_filtered[icustays_filtered["first_careunit"] == icustays_filtered["last_careunit"]]
    icustays_filtered = icustays_filtered[icustays_filtered["los"] >= consts.MINIMAL_LOS_DAYS]
    inputevents = inputevents.merge(icustays_filtered[["stay_id", "first_careunit"]], left_on="stay_id", right_on="stay_id")
    return inputevents