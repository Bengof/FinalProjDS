# FinalProjDS
### To unpack data from .gz to .csv format use:
	python3 unpack_data.py
### To create filtered files and prepare them for RNL, run:
	preprocess_eicu.py
	preprocess_mimic.py
### To train RNL on eICU or MIMIC, edit the variable data_path to be the path of the relevant preprocessed file in the following file:
	rnl.rnl_trainer.py
