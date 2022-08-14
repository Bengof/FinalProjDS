from enum import Enum

class State(Enum):
    OK = 0,
    
    OVERLAPPED_WITH_DIFFERENT_MED = 2,
    OVERLAPPED_WITH_ANOTHER_NE_CHANGED_DOSE = 3,
    OVERLAPPED_WITH_ANOTHER_NE_STOPPED = 4,
    OVERLAPPED_WITH_ANOTHER_NE_PAUSED = 5,
    OVERLAPPED_WITH_ANOTHER_NE_FINISHED = 6,
    LESS_THAN_EPSILON_CHANGED_DOSE = 7,
    LESS_THAN_EPSILON_STOPPED = 8,
    LESS_THAN_EPSILON_PAUSED = 9,
    LESS_THAN_EPSILON_FINISHED = 10,
    SMALL_GAP_AND_SAME_RATE_STOPPED =11,
    SMALL_GAP_AND_SAME_RATE_PAUSED = 12,
    FINISHED_RUNNING = 13





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
MINIMAL_LOS_DAYS = 1 # minimal icu stay
MINIMAL_AGE =  20
MAXIMAL_AGE = 90

HOURS_BEFORE_DOSE = 1

BP_RANGES = ((0,44),(45,49),(50,54),(55,59),(60,64),(65,69),(70,74),(75,79),(80,84),(85,89),(90,94),(95,99),(100,104),(105,109),(110,114),(115,200))

# minimal gap between dose to previous dose in order to mark it as dose which is not a decision in Pause and Stopped statusdescription
MINIMAL_GAP_MINUTES = 2

PATH_TO_DATA = "../processed/"