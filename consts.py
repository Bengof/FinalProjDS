ICD_CODES = [5291, #
             4766, #
             3175, #
             2988] # TOP 4 sepsis icd codes
CHARTEVENTS_CODES = [225309, 225310, 225312, 220050, 220051, 220052, 220179, 220180, 220181] # ART + non invasive: BP, systolic, diastolic, mean,
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


