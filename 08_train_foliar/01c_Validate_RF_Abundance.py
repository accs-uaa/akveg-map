# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Validate random forest abundance model
# Author: Timm Nawrocki
# Last Updated: 2024-09-10
# Usage: Must be executed in an Anaconda Python 3.12+ installation.
# Description: "Validate random forest abundance model" validates a random forest classifier and regressor. The model validation accounts for spatial autocorrelation by grouping in 100 km blocks.
# ---------------------------------------------------------------------------

# Import packages
import numpy as np
import os
import pandas as pd
import time
from akutils import *
from sklearn.utils import shuffle
from sklearn.model_selection import StratifiedGroupKFold
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set round date
round_date = 'round_20240910'

# Define species
group = 'ndsalix'

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
extract_folder = os.path.join(drive, root_folder, 'Data_Input/extract_data')
species_folder = os.path.join(drive, root_folder, 'Data_Input/species_data')
output_folder = os.path.join(drive, root_folder, 'Data_Output/model_results', round_date, group)
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define input files
covariate_file = os.path.join(extract_folder, 'AKVEG_Sites_Covariates_3338.csv')
species_file = os.path.join(species_folder, f'cover_{group}_3338.csv')

# Define output files
output_file = os.path.join(output_folder, f'{group}_Results.csv')
auc_file = os.path.join(output_folder, f'{group}_AUC.txt')
acc_file = os.path.join(output_folder, f'{group}_ACC.txt')
threshold_file = os.path.join(output_folder, f'{group}_Threshold.txt')
rscore_file = os.path.join(output_folder, f'{group}_Rsquared.txt')
rmse_file = os.path.join(output_folder, f'{group}_RMSE.txt')
mae_file = os.path.join(output_folder, f'{group}_MAE.txt')

# Define variable sets
validation = ['valid']
predictor_all = ['summer', 'january', 'precip',
                 'coast', 'stream', 'river', 'wetness',
                 'elevation', 'exposure', 'heatload', 'position',
                 'aspect', 'relief', 'roughness', 'slope',
                 's1_1_vha', 's1_1_vhd', 's1_1_vva', 's1_1_vvd',
                 's1_2_vha', 's1_2_vhd', 's1_2_vva', 's1_2_vvd',
                 's1_3_vha', 's1_3_vhd', 's1_3_vva', 's1_3_vvd',
                 's2_1_blue', 's2_1_green', 's2_1_red', 's2_1_redge1', 's2_1_redge2',
                 's2_1_redge3', 's2_1_nir', 's2_1_redge4', 's2_1_swir1', 's2_1_swir2',
                 's2_1_nbr', 's2_1_ngrdi', 's2_1_ndmi', 's2_1_ndsi', 's2_1_ndvi', 's2_1_ndwi',
                 's2_1_bcc', 's2_1_gcc', 's2_1_rcc',
                 's2_2_blue', 's2_2_green', 's2_2_red', 's2_2_redge1', 's2_2_redge2',
                 's2_2_redge3', 's2_2_nir', 's2_2_redge4', 's2_2_swir1', 's2_2_swir2',
                 's2_2_nbr', 's2_2_ngrdi', 's2_2_ndmi', 's2_2_ndsi', 's2_2_ndvi', 's2_2_ndwi',
                 's2_2_bcc', 's2_2_gcc', 's2_2_rcc',
                 's2_3_blue', 's2_3_green', 's2_3_red', 's2_3_redge1', 's2_3_redge2',
                 's2_3_redge3', 's2_3_nir', 's2_3_redge4', 's2_3_swir1', 's2_3_swir2',
                 's2_3_nbr', 's2_3_ngrdi', 's2_3_ndmi', 's2_3_ndsi', 's2_3_ndvi', 's2_3_ndwi',
                 's2_3_bcc', 's2_3_gcc', 's2_3_rcc',
                 's2_4_blue', 's2_4_green', 's2_4_red', 's2_4_redge1', 's2_4_redge2',
                 's2_4_redge3', 's2_4_nir', 's2_4_redge4', 's2_4_swir1', 's2_4_swir2',
                 's2_4_nbr', 's2_4_ngrdi', 's2_4_ndmi', 's2_4_ndsi', 's2_4_ndvi', 's2_4_ndwi',
                 's2_4_bcc', 's2_4_gcc', 's2_4_rcc',
                 's2_5_blue', 's2_5_green', 's2_5_red', 's2_5_redge1', 's2_5_redge2',
                 's2_5_redge3', 's2_5_nir', 's2_5_redge4', 's2_5_swir1', 's2_5_swir2',
                 's2_5_nbr', 's2_5_ngrdi', 's2_5_ndmi', 's2_5_ndsi', 's2_5_ndvi', 's2_5_ndwi',
                 's2_5_bcc', 's2_5_gcc', 's2_5_rcc',
                 's2_rng_blue', 's2_rng_green', 's2_rng_red', 's2_rng_redge1', 's2_rng_redge2',
                 's2_rng_redge3', 's2_rng_nir', 's2_rng_redge4', 's2_rng_swir1', 's2_rng_swir2',
                 's2_rng_nbr', 's2_rng_ngrdi', 's2_rng_ndmi', 's2_rng_ndsi', 's2_rng_ndvi', 's2_rng_ndwi',
                 's2_std_blue', 's2_std_green', 's2_std_red', 's2_std_redge1', 's2_std_redge2',
                 's2_std_redge3', 's2_std_nir', 's2_std_redge4', 's2_std_swir1', 's2_std_swir2',
                 's2_std_nbr', 's2_std_ngrdi', 's2_std_ndmi', 's2_std_ndsi', 's2_std_ndvi', 's2_std_ndwi'
                 ]
obs_pres = ['presence']
obs_cover = ['cvr_pct']
retain_variables = ['st_vst'] + validation
all_variables = retain_variables + predictor_all + obs_pres + obs_cover
outer_split = ['outer_split_n']
inner_split = ['inner_split_n']
pred_abs = ['pred_abs']
pred_pres = ['pred_pres']
pred_bin = ['pred_bin']
pred_cover = ['pred_cover']
prediction = ['prediction']
inner_columns = all_variables + pred_abs + pred_pres + inner_split
outer_columns = all_variables + pred_abs + pred_pres + pred_cover + pred_bin + outer_split

# Create a standardized parameter set for a random forest classifier
classifier_params = {'n_estimators': 500,
                     'criterion': 'gini',
                     'max_depth': None,
                     'min_samples_split': 2,
                     'min_samples_leaf': 1,
                     'min_weight_fraction_leaf': 0,
                     'max_features': 'sqrt',
                     'bootstrap': True,
                     'oob_score': False,
                     'sampling_strategy': 'all',
                     'replacement': True,
                     'warm_start': False,
                     'class_weight': None,
                     'n_jobs': 2,
                     'random_state': 314}

# Create a standardized parameter set for a random forest classifier
regressor_params = {'n_estimators': 500,
                    'criterion': 'poisson',
                    'max_depth': None,
                    'min_samples_split': 2,
                    'min_samples_leaf': 1,
                    'min_weight_fraction_leaf': 0,
                    'max_features': 'sqrt',
                    'bootstrap': True,
                    'oob_score': False,
                    'warm_start': True,
                    'n_jobs': 2,
                    'random_state': 314}

# Define cross validation methods
outer_cv_splits = StratifiedGroupKFold(n_splits=10)
inner_cv_splits = StratifiedGroupKFold(n_splits=10)

#### PREPARE INPUT DATA
####____________________________________________________

# Read input data to data frames
print('Loading input data...')
iteration_start = time.time()
covariate_data = pd.read_csv(covariate_file)
species_data = pd.read_csv(species_file)[['st_vst', 'cvr_pct', 'presence', 'valid']]

# Calculate derived metrics for season 1
covariate_data['s2_1_nbr'] = ((covariate_data['s2_1_nir'] - covariate_data['s2_1_swir2'])
                              / (covariate_data['s2_1_nir'] + covariate_data['s2_1_swir2']))
covariate_data['s2_1_ngrdi'] = ((covariate_data['s2_1_green'] - covariate_data['s2_1_red'])
                                / (covariate_data['s2_1_green'] + covariate_data['s2_1_red']))
covariate_data['s2_1_ndmi'] = ((covariate_data['s2_1_nir'] - covariate_data['s2_1_swir1'])
                               / (covariate_data['s2_1_nir'] + covariate_data['s2_1_swir1']))
covariate_data['s2_1_ndsi'] = ((covariate_data['s2_1_green'] - covariate_data['s2_1_swir1'])
                               / (covariate_data['s2_1_green'] + covariate_data['s2_1_swir1']))
covariate_data['s2_1_ndvi'] = ((covariate_data['s2_1_nir'] - covariate_data['s2_1_red'])
                               / (covariate_data['s2_1_nir'] + covariate_data['s2_1_red']))
covariate_data['s2_1_ndwi'] = ((covariate_data['s2_1_green'] - covariate_data['s2_1_nir'])
                               / (covariate_data['s2_1_green'] + covariate_data['s2_1_nir']))
covariate_data['s2_1_bcc'] = (covariate_data['s2_1_blue']
                              / (covariate_data['s2_1_blue'] + covariate_data['s2_1_green']
                                 + covariate_data['s2_1_red']))
covariate_data['s2_1_gcc'] = (covariate_data['s2_1_green']
                              / (covariate_data['s2_1_blue'] + covariate_data['s2_1_green']
                                 + covariate_data['s2_1_red']))
covariate_data['s2_1_rcc'] = (covariate_data['s2_1_red']
                              / (covariate_data['s2_1_blue'] + covariate_data['s2_1_green']
                                 + covariate_data['s2_1_red']))

# Calculate derived metrics for season 2
covariate_data['s2_2_nbr'] = ((covariate_data['s2_2_nir'] - covariate_data['s2_2_swir2'])
                              / (covariate_data['s2_2_nir'] + covariate_data['s2_2_swir2']))
covariate_data['s2_2_ngrdi'] = ((covariate_data['s2_2_green'] - covariate_data['s2_2_red'])
                                / (covariate_data['s2_2_green'] + covariate_data['s2_2_red']))
covariate_data['s2_2_ndmi'] = ((covariate_data['s2_2_nir'] - covariate_data['s2_2_swir1'])
                               / (covariate_data['s2_2_nir'] + covariate_data['s2_2_swir1']))
covariate_data['s2_2_ndsi'] = ((covariate_data['s2_2_green'] - covariate_data['s2_2_swir1'])
                               / (covariate_data['s2_2_green'] + covariate_data['s2_2_swir1']))
covariate_data['s2_2_ndvi'] = ((covariate_data['s2_2_nir'] - covariate_data['s2_2_red'])
                               / (covariate_data['s2_2_nir'] + covariate_data['s2_2_red']))
covariate_data['s2_2_ndwi'] = ((covariate_data['s2_2_green'] - covariate_data['s2_2_nir'])
                               / (covariate_data['s2_2_green'] + covariate_data['s2_2_nir']))
covariate_data['s2_2_bcc'] = (covariate_data['s2_2_blue']
                              / (covariate_data['s2_2_blue'] + covariate_data['s2_2_green']
                                 + covariate_data['s2_2_red']))
covariate_data['s2_2_gcc'] = (covariate_data['s2_2_green']
                              / (covariate_data['s2_2_blue'] + covariate_data['s2_2_green']
                                 + covariate_data['s2_2_red']))
covariate_data['s2_2_rcc'] = (covariate_data['s2_2_red']
                              / (covariate_data['s2_2_blue'] + covariate_data['s2_2_green']
                                 + covariate_data['s2_2_red']))

# Calculate derived metrics for season 3
covariate_data['s2_3_nbr'] = ((covariate_data['s2_3_nir'] - covariate_data['s2_3_swir2'])
                              / (covariate_data['s2_3_nir'] + covariate_data['s2_3_swir2']))
covariate_data['s2_3_ngrdi'] = ((covariate_data['s2_3_green'] - covariate_data['s2_3_red'])
                                / (covariate_data['s2_3_green'] + covariate_data['s2_3_red']))
covariate_data['s2_3_ndmi'] = ((covariate_data['s2_3_nir'] - covariate_data['s2_3_swir1'])
                               / (covariate_data['s2_3_nir'] + covariate_data['s2_3_swir1']))
covariate_data['s2_3_ndsi'] = ((covariate_data['s2_3_green'] - covariate_data['s2_3_swir1'])
                               / (covariate_data['s2_3_green'] + covariate_data['s2_3_swir1']))
covariate_data['s2_3_ndvi'] = ((covariate_data['s2_3_nir'] - covariate_data['s2_3_red'])
                               / (covariate_data['s2_3_nir'] + covariate_data['s2_3_red']))
covariate_data['s2_3_ndwi'] = ((covariate_data['s2_3_green'] - covariate_data['s2_3_nir'])
                               / (covariate_data['s2_3_green'] + covariate_data['s2_3_nir']))
covariate_data['s2_3_bcc'] = (covariate_data['s2_3_blue']
                              / (covariate_data['s2_3_blue'] + covariate_data['s2_3_green']
                                 + covariate_data['s2_3_red']))
covariate_data['s2_3_gcc'] = (covariate_data['s2_3_green']
                              / (covariate_data['s2_3_blue'] + covariate_data['s2_3_green']
                                 + covariate_data['s2_3_red']))
covariate_data['s2_3_rcc'] = (covariate_data['s2_3_red']
                              / (covariate_data['s2_3_blue'] + covariate_data['s2_3_green']
                                 + covariate_data['s2_3_red']))

# Calculate derived metrics for season 4
covariate_data['s2_4_nbr'] = ((covariate_data['s2_4_nir'] - covariate_data['s2_4_swir2'])
                              / (covariate_data['s2_4_nir'] + covariate_data['s2_4_swir2']))
covariate_data['s2_4_ngrdi'] = ((covariate_data['s2_4_green'] - covariate_data['s2_4_red'])
                                / (covariate_data['s2_4_green'] + covariate_data['s2_4_red']))
covariate_data['s2_4_ndmi'] = ((covariate_data['s2_4_nir'] - covariate_data['s2_4_swir1'])
                               / (covariate_data['s2_4_nir'] + covariate_data['s2_4_swir1']))
covariate_data['s2_4_ndsi'] = ((covariate_data['s2_4_green'] - covariate_data['s2_4_swir1'])
                               / (covariate_data['s2_4_green'] + covariate_data['s2_4_swir1']))
covariate_data['s2_4_ndvi'] = ((covariate_data['s2_4_nir'] - covariate_data['s2_4_red'])
                               / (covariate_data['s2_4_nir'] + covariate_data['s2_4_red']))
covariate_data['s2_4_ndwi'] = ((covariate_data['s2_4_green'] - covariate_data['s2_4_nir'])
                               / (covariate_data['s2_4_green'] + covariate_data['s2_4_nir']))
covariate_data['s2_4_bcc'] = (covariate_data['s2_4_blue']
                              / (covariate_data['s2_4_blue'] + covariate_data['s2_4_green']
                                 + covariate_data['s2_4_red']))
covariate_data['s2_4_gcc'] = (covariate_data['s2_4_green']
                              / (covariate_data['s2_4_blue'] + covariate_data['s2_4_green']
                                 + covariate_data['s2_4_red']))
covariate_data['s2_4_rcc'] = (covariate_data['s2_4_red']
                              / (covariate_data['s2_4_blue'] + covariate_data['s2_4_green']
                                 + covariate_data['s2_4_red']))

# Calculate derived metrics for season 5
covariate_data['s2_5_nbr'] = ((covariate_data['s2_5_nir'] - covariate_data['s2_5_swir2'])
                              / (covariate_data['s2_5_nir'] + covariate_data['s2_5_swir2']))
covariate_data['s2_5_ngrdi'] = ((covariate_data['s2_5_green'] - covariate_data['s2_5_red'])
                                / (covariate_data['s2_5_green'] + covariate_data['s2_5_red']))
covariate_data['s2_5_ndmi'] = ((covariate_data['s2_5_nir'] - covariate_data['s2_5_swir1'])
                               / (covariate_data['s2_5_nir'] + covariate_data['s2_5_swir1']))
covariate_data['s2_5_ndsi'] = ((covariate_data['s2_5_green'] - covariate_data['s2_5_swir1'])
                               / (covariate_data['s2_5_green'] + covariate_data['s2_5_swir1']))
covariate_data['s2_5_ndvi'] = ((covariate_data['s2_5_nir'] - covariate_data['s2_5_red'])
                               / (covariate_data['s2_5_nir'] + covariate_data['s2_5_red']))
covariate_data['s2_5_ndwi'] = ((covariate_data['s2_5_green'] - covariate_data['s2_5_nir'])
                               / (covariate_data['s2_5_green'] + covariate_data['s2_5_nir']))
covariate_data['s2_5_bcc'] = (covariate_data['s2_5_blue']
                              / (covariate_data['s2_5_blue'] + covariate_data['s2_5_green']
                                 + covariate_data['s2_5_red']))
covariate_data['s2_5_gcc'] = (covariate_data['s2_5_green']
                              / (covariate_data['s2_5_blue'] + covariate_data['s2_5_green']
                                 + covariate_data['s2_5_red']))
covariate_data['s2_5_rcc'] = (covariate_data['s2_5_red']
                              / (covariate_data['s2_5_blue'] + covariate_data['s2_5_green']
                                 + covariate_data['s2_5_red']))

# Create seasonal range metrics
covariate_data['s2_rng_blue'] = (covariate_data['s2_3_blue'] -
                                 np.mean([covariate_data['s2_1_blue'], covariate_data['s2_2_blue'],
                                          covariate_data['s2_4_blue'], covariate_data['s2_5_blue']]))
covariate_data['s2_rng_green'] = (covariate_data['s2_3_green'] -
                                  np.mean([covariate_data['s2_1_green'], covariate_data['s2_2_green'],
                                           covariate_data['s2_4_green'], covariate_data['s2_5_green']]))
covariate_data['s2_rng_red'] = (covariate_data['s2_3_red'] -
                                np.mean([covariate_data['s2_1_red'], covariate_data['s2_2_red'],
                                         covariate_data['s2_4_red'], covariate_data['s2_5_red']]))
covariate_data['s2_rng_redge1'] = (covariate_data['s2_3_redge1'] -
                                 np.mean([covariate_data['s2_1_redge1'], covariate_data['s2_2_redge1'],
                                          covariate_data['s2_4_redge1'], covariate_data['s2_5_redge1']]))
covariate_data['s2_rng_redge2'] = (covariate_data['s2_3_redge2'] -
                                 np.mean([covariate_data['s2_1_redge2'], covariate_data['s2_2_redge2'],
                                          covariate_data['s2_4_redge2'], covariate_data['s2_5_redge2']]))
covariate_data['s2_rng_redge3'] = (covariate_data['s2_3_redge3'] -
                                 np.mean([covariate_data['s2_1_redge3'], covariate_data['s2_2_redge3'],
                                          covariate_data['s2_4_redge3'], covariate_data['s2_5_redge3']]))
covariate_data['s2_rng_nir'] = (covariate_data['s2_3_nir'] -
                                 np.mean([covariate_data['s2_1_nir'], covariate_data['s2_2_nir'],
                                          covariate_data['s2_4_nir'], covariate_data['s2_5_nir']]))
covariate_data['s2_rng_redge4'] = (covariate_data['s2_3_redge4'] -
                                 np.mean([covariate_data['s2_1_redge4'], covariate_data['s2_2_redge4'],
                                          covariate_data['s2_4_redge4'], covariate_data['s2_5_redge4']]))
covariate_data['s2_rng_swir1'] = (covariate_data['s2_3_swir1'] -
                                 np.mean([covariate_data['s2_1_swir1'], covariate_data['s2_2_swir1'],
                                          covariate_data['s2_4_swir1'], covariate_data['s2_5_swir1']]))
covariate_data['s2_rng_swir2'] = (covariate_data['s2_3_swir2'] -
                                 np.mean([covariate_data['s2_1_swir2'], covariate_data['s2_2_swir2'],
                                          covariate_data['s2_4_swir2'], covariate_data['s2_5_swir2']]))
covariate_data['s2_rng_nbr'] = (covariate_data['s2_3_nbr'] -
                                 np.mean([covariate_data['s2_1_nbr'], covariate_data['s2_2_nbr'],
                                          covariate_data['s2_4_nbr'], covariate_data['s2_5_nbr']]))
covariate_data['s2_rng_ngrdi'] = (covariate_data['s2_3_ngrdi'] -
                                 np.mean([covariate_data['s2_1_ngrdi'], covariate_data['s2_2_ngrdi'],
                                          covariate_data['s2_4_ngrdi'], covariate_data['s2_5_ngrdi']]))
covariate_data['s2_rng_ndmi'] = (covariate_data['s2_3_ndmi'] -
                                 np.mean([covariate_data['s2_1_ndmi'], covariate_data['s2_2_ndmi'],
                                          covariate_data['s2_4_ndmi'], covariate_data['s2_5_ndmi']]))
covariate_data['s2_rng_ndsi'] = (covariate_data['s2_3_ndsi'] -
                                 np.mean([covariate_data['s2_1_ndsi'], covariate_data['s2_2_ndsi'],
                                          covariate_data['s2_4_ndsi'], covariate_data['s2_5_ndsi']]))
covariate_data['s2_rng_ndvi'] = (covariate_data['s2_3_ndvi'] -
                                 np.mean([covariate_data['s2_1_ndvi'], covariate_data['s2_2_ndvi'],
                                          covariate_data['s2_4_ndvi'], covariate_data['s2_5_ndvi']]))
covariate_data['s2_rng_ndwi'] = (covariate_data['s2_3_ndwi'] -
                                 np.mean([covariate_data['s2_1_ndwi'], covariate_data['s2_2_ndwi'],
                                          covariate_data['s2_4_ndwi'], covariate_data['s2_5_ndwi']]))
covariate_data['s2_std_blue'] = np.std([covariate_data['s2_1_blue'], covariate_data['s2_2_blue'],
                                        covariate_data['s2_3_blue'], covariate_data['s2_4_blue'],
                                        covariate_data['s2_5_blue']])
covariate_data['s2_std_green'] = np.std([covariate_data['s2_1_green'], covariate_data['s2_2_green'],
                                        covariate_data['s2_3_green'], covariate_data['s2_4_green'],
                                        covariate_data['s2_5_green']])
covariate_data['s2_std_red'] = np.std([covariate_data['s2_1_red'], covariate_data['s2_2_red'],
                                        covariate_data['s2_3_red'], covariate_data['s2_4_red'],
                                        covariate_data['s2_5_red']])
covariate_data['s2_std_redge1'] = np.std([covariate_data['s2_1_redge1'], covariate_data['s2_2_redge1'],
                                        covariate_data['s2_3_redge1'], covariate_data['s2_4_redge1'],
                                        covariate_data['s2_5_redge1']])
covariate_data['s2_std_redge2'] = np.std([covariate_data['s2_1_redge2'], covariate_data['s2_2_redge2'],
                                        covariate_data['s2_3_redge2'], covariate_data['s2_4_redge2'],
                                        covariate_data['s2_5_redge2']])
covariate_data['s2_std_redge3'] = np.std([covariate_data['s2_1_redge3'], covariate_data['s2_2_redge3'],
                                        covariate_data['s2_3_redge3'], covariate_data['s2_4_redge3'],
                                        covariate_data['s2_5_redge3']])
covariate_data['s2_std_nir'] = np.std([covariate_data['s2_1_nir'], covariate_data['s2_2_nir'],
                                        covariate_data['s2_3_nir'], covariate_data['s2_4_nir'],
                                        covariate_data['s2_5_nir']])
covariate_data['s2_std_redge4'] = np.std([covariate_data['s2_1_redge4'], covariate_data['s2_2_redge4'],
                                        covariate_data['s2_3_redge4'], covariate_data['s2_4_redge4'],
                                        covariate_data['s2_5_redge4']])
covariate_data['s2_std_swir1'] = np.std([covariate_data['s2_1_swir1'], covariate_data['s2_2_swir1'],
                                        covariate_data['s2_3_swir1'], covariate_data['s2_4_swir1'],
                                        covariate_data['s2_5_swir1']])
covariate_data['s2_std_swir2'] = np.std([covariate_data['s2_1_swir2'], covariate_data['s2_2_swir2'],
                                        covariate_data['s2_3_swir2'], covariate_data['s2_4_swir2'],
                                        covariate_data['s2_5_swir2']])
covariate_data['s2_std_nbr'] = np.std([covariate_data['s2_1_nbr'], covariate_data['s2_2_nbr'],
                                        covariate_data['s2_3_nbr'], covariate_data['s2_4_nbr'],
                                        covariate_data['s2_5_nbr']])
covariate_data['s2_std_ngrdi'] = np.std([covariate_data['s2_1_ngrdi'], covariate_data['s2_2_ngrdi'],
                                        covariate_data['s2_3_ngrdi'], covariate_data['s2_4_ngrdi'],
                                        covariate_data['s2_5_ngrdi']])
covariate_data['s2_std_ndmi'] = np.std([covariate_data['s2_1_ndmi'], covariate_data['s2_2_ndmi'],
                                        covariate_data['s2_3_ndmi'], covariate_data['s2_4_ndmi'],
                                        covariate_data['s2_5_ndmi']])
covariate_data['s2_std_ndsi'] = np.std([covariate_data['s2_1_ndsi'], covariate_data['s2_2_ndsi'],
                                        covariate_data['s2_3_ndsi'], covariate_data['s2_4_ndsi'],
                                        covariate_data['s2_5_ndsi']])
covariate_data['s2_std_ndvi'] = np.std([covariate_data['s2_1_ndvi'], covariate_data['s2_2_ndvi'],
                                        covariate_data['s2_3_ndvi'], covariate_data['s2_4_ndvi'],
                                        covariate_data['s2_5_ndvi']])
covariate_data['s2_std_ndwi'] = np.std([covariate_data['s2_1_ndwi'], covariate_data['s2_2_ndwi'],
                                        covariate_data['s2_3_ndwi'], covariate_data['s2_4_ndwi'],
                                        covariate_data['s2_5_ndwi']])

# Create an inner join of species and covariate data
input_data = species_data.merge(covariate_data, how='inner', on='st_vst')

# Create empty lists to store threshold and performance metrics
auc_list = []
accuracy_list = []
classifier_list = []

# Shuffle data
shuffled_data = shuffle(input_data, random_state=314).copy()

# Create an empty data frame to store the outer cross validation splits
outer_train = pd.DataFrame(columns=all_variables + outer_split)
outer_test = pd.DataFrame(columns=all_variables + outer_split)
end_timing(iteration_start)

# Create outer cross validation splits
print('Creating outer cross validation splits...')
iteration_start = time.time()
count = 1
for train_index, test_index in outer_cv_splits.split(shuffled_data,
                                                     shuffled_data[obs_pres[0]].astype('int32'),
                                                     shuffled_data[validation[0]].astype('int32')):
    # Split the data into train and test partitions
    train = shuffled_data.iloc[train_index]
    test = shuffled_data.iloc[test_index]
    # Insert outer_cv_split_n to train
    train = train.assign(outer_split_n=count)
    # Insert outer_cv_split_n to test
    test = test.assign(outer_split_n=count)
    # Append to data frames
    outer_train = pd.concat([outer_train if not outer_train.empty else None,
                             train],
                            axis=0)
    outer_test = pd.concat([outer_test if not outer_test.empty else None,
                            test],
                           axis=0)
    # Increase counter
    count += 1
outer_cv_length = count - 1

# Reset indices
outer_train = outer_train.reset_index()
outer_test = outer_test.reset_index()
print(f'Created {outer_cv_length} outer cross-validation group splits.')

# Create an empty data frame to store the outer test results
outer_results = pd.DataFrame(columns=outer_columns)
end_timing(iteration_start)

#### CONDUCT MODEL VALIDATION
####____________________________________________________

threshold_list = []

# Iterate through outer cross validation splits
outer_cv_i = 1
while outer_cv_i <= outer_cv_length:
    print(f'Conducting outer cross-validation iteration {outer_cv_i} of {outer_cv_length}...')
    iteration_start = time.time()

    #### SETUP INNER DATA
    ####____________________________________________________
    print('\tCreating inner cross validation splits...')
    # Partition the outer train split by iteration number
    outer_train_iteration = outer_train[outer_train[outer_split[0]] == outer_cv_i].copy()
    outer_test_iteration = outer_test[outer_test[outer_split[0]] == outer_cv_i].copy()

    # Create an empty data frame to store the inner cross validation splits
    inner_train = pd.DataFrame(columns=all_variables + inner_split)
    inner_test = pd.DataFrame(columns=all_variables + inner_split)

    # Create an empty data frame to store the inner test results
    inner_results = pd.DataFrame(columns=all_variables + pred_abs + pred_pres + ['inner_cv_split_n'])

    # Create inner cross validation splits
    count = 1
    for train_index, test_index in inner_cv_splits.split(outer_train_iteration,
                                                         outer_train_iteration[obs_pres[0]].astype('int32'),
                                                         outer_train_iteration[validation[0]].astype('int32')):
        # Split the data into train and test partitions
        train = outer_train_iteration.iloc[train_index]
        test = outer_train_iteration.iloc[test_index]
        # Insert iteration to train
        train = train.assign(inner_split_n=count)
        # Insert iteration to test
        test = test.assign(inner_split_n=count)
        # Append to data frames
        inner_train = pd.concat([inner_train if not inner_train.empty else None,
                                 train],
                                axis=0)
        inner_test = pd.concat([inner_test if not inner_test.empty else None,
                                test],
                               axis=0)
        # Increase counter
        count += 1
    inner_cv_length = count - 1

    # Reset indices
    inner_train = inner_train.reset_index()
    inner_test = inner_test.reset_index()

    #### CONDUCT INNER THRESHOLD DETERMINATION
    ####____________________________________________________

    # Iterate through inner cross validation splits
    inner_cv_i = 1
    while inner_cv_i <= inner_cv_length:
        print(f'\tConducting inner cross validation iteration {inner_cv_i} of {inner_cv_length}...')
        inner_train_iteration = inner_train[inner_train[inner_split[0]] == inner_cv_i].copy()
        inner_test_iteration = inner_test[inner_test[inner_split[0]] == inner_cv_i].copy()

        # Identify X and y inner train and test splits
        X_class_inner = inner_train_iteration[predictor_all].astype(float).copy()
        y_class_inner = inner_train_iteration[obs_pres[0]].astype('int32').copy()
        X_test_inner = inner_test_iteration[predictor_all].astype(float).copy()

        # Train classifier on the inner train data
        print('\t\tTraining inner classifier...')
        inner_classifier = BalancedRandomForestClassifier(**classifier_params)
        inner_classifier.fit(X_class_inner, y_class_inner)

        # Predict inner test data
        print('\t\tPredicting inner cross-validation test data...')
        probability_inner = inner_classifier.predict_proba(X_test_inner)

        # Assign predicted values to inner test data frame
        inner_test_iteration = inner_test_iteration.assign(pred_abs=probability_inner[:, 0])
        inner_test_iteration = inner_test_iteration.assign(pred_pres=probability_inner[:, 1])

        # Add the test results to output data frame
        inner_results = pd.concat([inner_results if not inner_results.empty else None,
                                   inner_test_iteration],
                                  axis=0)

        # Increase n value
        inner_cv_i += 1

    # Calculate the optimal threshold and performance of the presence-absence classification
    print('\tOptimizing classification threshold...')
    threshold, sensitivity, specificity, auc, accuracy = determine_optimal_threshold(
        inner_results[pred_pres[0]],
        inner_results[obs_pres[0]]
    )
    threshold_list.append(threshold)

    #### CONDUCT OUTER CROSS VALIDATION
    ####____________________________________________________

    # Identify X and y train splits for the classifier
    X_class_outer = outer_train_iteration[predictor_all].astype(float).copy()
    y_class_outer = outer_train_iteration[obs_pres[0]].astype('int32').copy()
    X_test_outer = outer_test_iteration[predictor_all].astype(float).copy()

    # Train classifier on the outer train data
    print('\tTraining outer classifier...')
    outer_classifier = BalancedRandomForestClassifier(**classifier_params)
    outer_classifier.fit(X_class_outer, y_class_outer)

    # Train regressor on the outer train data
    print('\tTraining outer regressor...')
    outer_regressor = RandomForestRegressor(**regressor_params)
    X_regress_outer = outer_train_iteration[predictor_all].astype(float).copy()
    y_regress_outer = outer_train_iteration[obs_cover[0]].astype(float).copy()
    outer_regressor.fit(X_regress_outer, y_regress_outer)

    # Predict inner test data
    print('\tPredicting outer cross-validation test data...')
    probability_outer = outer_classifier.predict_proba(X_test_outer)
    cover_outer = outer_regressor.predict(X_test_outer)

    # Assign predicted values to outer test data frame
    outer_test_iteration = outer_test_iteration.assign(pred_abs=probability_outer[:, 0])
    outer_test_iteration = outer_test_iteration.assign(pred_pres=probability_outer[:, 1])
    outer_test_iteration = outer_test_iteration.assign(pred_cover=cover_outer)

    # Convert probability to presence-absence
    presence_zeros = np.zeros(outer_test_iteration[pred_pres[0]].shape)
    presence_zeros[outer_test_iteration[pred_pres[0]] >= threshold] = 1

    # Assign binary prediction values to test data frame
    outer_test_iteration = outer_test_iteration.assign(pred_bin=presence_zeros)

    # Add the test results to output data frame
    outer_results = pd.concat([outer_results if not outer_results.empty else None,
                               outer_test_iteration],
                              axis=0)
    end_timing(iteration_start)

    # Increase iteration number
    outer_cv_i += 1

#### CALCULATE PERFORMANCE AND STORE RESULTS
####____________________________________________________

# Create a composite prediction
outer_results[prediction[0]] = np.where((outer_results[pred_bin[0]] == 1)
                                        & (outer_results[pred_cover[0]] >= 0.5),
                                        outer_results[pred_cover[0]],
                                        0)
outer_results['distribution'] = np.where((outer_results[pred_bin[0]] == 1)
                                         & (outer_results[pred_cover[0]] >= 0.5),
                                         1,
                                         0)

# Partition output results to presence-absence observed and predicted
y_classify_observed = outer_results[obs_pres[0]].astype('int32').copy()
y_classify_predicted = outer_results['distribution'].astype('int32').copy()
y_classify_probability = outer_results[pred_pres[0]].astype(float).copy()

# Partition output results to foliar cover observed and predicted
y_regress_observed = outer_results[obs_cover[0]].astype(float).copy()
y_regress_predicted = outer_results[prediction[0]].astype(float).copy()

# Determine error rates
confusion_test = confusion_matrix(y_classify_observed, y_classify_predicted)
true_negative = confusion_test[0, 0]
false_negative = confusion_test[1, 0]
true_positive = confusion_test[1, 1]
false_positive = confusion_test[0, 1]

# Calculate metrics
validation_auc = roc_auc_score(y_classify_observed, y_classify_probability)
validation_accuracy = (true_negative + true_positive) / (
        true_negative + false_positive + false_negative + true_positive)

# Calculate performance metrics from output_results
r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

# Modify metrics for export
export_auc = round(validation_auc, 3)
export_accuracy = round(validation_accuracy * 100, 1)
export_threshold = round(np.mean(threshold_list), 5)
export_rscore = round(r_score, 3)
export_rmse = round(rmse, 1)
export_mae = round(mae, 1)

# Store output results in csv file
print('Writing output files...')
iteration_start = time.time()
outer_results.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
output_list = [auc_file, acc_file, threshold_file, rscore_file, rmse_file, mae_file]
metric_list = [export_auc, export_accuracy, export_threshold, export_rscore, export_rmse, export_mae]
count = 0
for metric in metric_list:
    output_file = output_list[count]
    file = open(output_file, 'w')
    file.write(str(metric))
    file.close()
    count += 1
end_timing(iteration_start)

# Print scores
print(f'AUC: {export_auc}')
print(f'ACC: {export_accuracy}')
print(f'Threshold: {export_threshold}')
print(f'R-squared: {export_rscore}')
print(f'RMSE: {export_rmse}')
print(f'MAE: {export_mae}')
