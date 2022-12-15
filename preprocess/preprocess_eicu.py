from consts import *
from preprocess.chunk_filtering import filter_big_file
from preprocess.preprocess_mimic import generate_rnl_states_and_actions
import pandas as pd


def contains_sepsis(value):
    for icd in EICU_SEPSIS_ICD_CODES:
        if value.lower().find(icd) != -1:
            return True
    return False


def filter_diagnosis(diagnosis):
    diagnosis = diagnosis[~diagnosis["icd9code"].isna()]
    diagnosis_filtered = diagnosis[diagnosis.apply(lambda row: contains_sepsis(row["icd9code"]), axis=1)]
    sepsis_patietns = diagnosis_filtered["patientunitstayid"].unique()
    return sepsis_patietns


def filter_infusiondrug(infusion_drug):
    drug_mcg_kg_min = infusion_drug[(infusion_drug["drugname"] == "Norepinephrine (mcg/kg/min)")]
    drug_mcg_kg_min["drugrate"] = drug_mcg_kg_min["drugrate"].astype("float")
    drug_mcg_min = infusion_drug[infusion_drug["drugname"] == "Norepinephrine (mcg/min)"]
    drug_mcg_min = drug_mcg_min.drop(drug_mcg_min.index[186664])
    drug_mcg_min["drugrate"] = drug_mcg_min["drugrate"].str.replace("Documentation undone", "0")
    drug_mcg_min["drugrate"] = drug_mcg_min["drugrate"].astype(float)
    drug_mcg_min["drugrate"] = drug_mcg_min["drugrate"] / drug_mcg_min["admissionweight"]
    drugs_converted = pd.concat([drug_mcg_min, drug_mcg_kg_min])
    drugs_converted = drugs_converted[["patientunitstayid", "infusionoffset", "drugrate"]]
    drugs_in_mimic_format = drugs_converted.rename(
        columns={"patientunitstayid": "stay_id", "infusionoffset": "starttime", "drugrate": "originalrate"})
    drugs_in_mimic_format["endtime"] = drugs_in_mimic_format["starttime"]
    return drugs_in_mimic_format


def filter_bp(bp_path, sepsis_stay_ids):
    filtered_bp = filter_big_file(bp_path,
                                  sepsis_stay_ids,
                                 subject_id_col_name="patientunitstayid")
    filtered_bp = filtered_bp[~filtered_bp["systemicmean"].isna()]
    filtered_bp = filtered_bp[["patientunitstayid", "observationoffset", "systemicmean"]]
    filtered_bp = filtered_bp.rename(
        columns={"patientunitstayid": "stay_id",
                 "observationoffset": "cur_bp_time",
                 "systemicmean": "cur_bp"})
    filtered_bp.loc[(filtered_bp["cur_bp"] >= 200), "cur_bp"] = 199
    filtered_bp.loc[(filtered_bp["cur_bp"] <= 0), "cur_bp"] = 0
    return filtered_bp


if '__main__' == __name__:
    # read files
    infusiondrug = pd.read_csv("../data/eICU/infusiondrug.csv")
    diagnosis = pd.read_csv("../data/eICU/diagnosis.csv")
    patients_weight = pd.read_csv("../data/eICU/patient.csv")[["patientunitstayid", "admissionweight"]]
    infusiondrug = infusiondrug.merge(patients_weight, on="patientunitstayid")

    # filter files
    sepsis_stay_ids = filter_diagnosis(diagnosis)
    filtered_bp = filter_bp("../data/eICU/vitalPeriodic.csv", sepsis_stay_ids)
    filtered_bp.to_csv("filtered_bp_eicu.csv")
    filtered_bp = pd.read_csv("filtered_bp_eicu.csv")
    filtered_drugs = filter_infusiondrug(infusiondrug)
    filtered_bp = filtered_bp[filtered_bp["stay_id"].isin(filtered_drugs["stay_id"].unique())]
    stay_ids = filtered_bp.groupby(by="stay_id").agg({"cur_bp": "count"})
    stay_ids_with_enough_events = stay_ids[stay_ids["cur_bp"] > 10].index
    filtered_bp = filtered_bp[filtered_bp["stay_id"].isin(stay_ids_with_enough_events)]

    #generate State - Action - State triples
    bps_and_dose = generate_rnl_states_and_actions(filtered_bp, filtered_drugs)
    bps_and_dose = bps_and_dose.rename(columns={"originalrate": "dose"})

    # filter out garbage
    bps_and_dose_thresh = bps_and_dose[(bps_and_dose["cur_bp"] < 180) | (bps_and_dose["last"])]
    bps_and_dose_thresh = bps_and_dose_thresh[(bps_and_dose_thresh["cur_bp"] > 20 | (bps_and_dose_thresh["first"]))]

    # write
    bps_and_dose_thresh.to_csv("../processed/RNLData/full_eICU_bps_with_doses.csv")
