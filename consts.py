ICD_CODES = ["99592", # Severe sepsis, icd_version =  9
             "R652", # Severe sepsis, icd_version = 10
             "R6520", # Severe sepsis, icd_version = 10
             "R6521",  # Severe sepsis with septic shock, icd_version = 10
             "99591" # Sepsis
             ]
BP = [#225309, # ART BP Systolic
    #225310, # ART BP Diastolic
    225312, # ART BP Mean
    #220050, # Arterial Blood Pressure systolic
    #220051, # Arterial Blood Pressure diastolic
    220052, # Arterial Blood Pressure mean	
    #220179, # Non Invasive Blood Pressure systolic
    #220180, # Non Invasive Blood Pressure diastolic
    220181 # Non Invasive Blood Pressure mean
    ]
HR = [220045] # Heart Rate
CHARTEVENTS_CODES = BP + HR
INPUTEVENTS_CODES = [
    221662, # Dopamine
    221289,	#Epinephrine
    221749,	#Phenylephrine
    221906,	#Norepinephrine
    229617,	#Epinephrine.
    229630,	#Phenylephrine (50/250)
    229631,	#Phenylephrine (200/250)_OLD_1
    229632,	#Phenylephrine (200/250)
    229789,	#Phenylephrine (Intubation)
    222315,	#Vasopressin
]
LABEVENTS_CODES = [
    50813,	#Lactate
    52442	#Lactate
]
PROCEDURE_CODES = [
    225792,  # invasive mechanical ventilation
    225441   # renal replacement therapy / dialysis
]
MINIMAL_LOS = 1 # minimal icu stay
MINIMAL_AGE =  20
MAXIMAL_AGE = 90

HOURS_BEFORE_DOSE = 1


