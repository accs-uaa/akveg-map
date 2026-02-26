# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Train statistical model for GEE
# Author: Timm Nawrocki
# Last Updated: 2024-07-31
# Usage: Must be executed in an Anaconda Python 3.12+ installation.
# Description: "Train statistical model for GEE" trains multiple sets of decision trees and uploads them as assets to GEE. The sets can subsequently be combined on GEE to create the final model.
# ---------------------------------------------------------------------------

# Define model targets
group = 'halgra'
version_date = '20260212'
presence_threshold = 3
predictor_names = ['clim', 'topo', 's1', 's2', 'emb']

# Import packages
import ee
import numpy as np
import os
import pandas as pd
import time
from geemap import ml
import joblib
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

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
site_folder = os.path.join(drive, root_folder,
                              f'Data_Input/site_data/version_{version_date}')
output_folder = os.path.join(drive, root_folder,
                             f'Data_Output/model_results/version_{version_date}/{group}')
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define input files
covariate_input = os.path.join(site_folder, 'akveg_site_visit_covariates.csv')

# Define output files for final model
threshold_output = os.path.join(output_folder, f'{group}_threshold_final.txt')
classifier_output = os.path.join(output_folder, f'{group}_classifier.joblib')
regressor_output = os.path.join(output_folder, f'{group}_regressor.joblib')
classifier_treestring_output = os.path.join(output_folder, f'{group}_classifier_treestring.txt')
regressor_treestring_output = os.path.join(output_folder, f'{group}_regressor_treestring.txt')

# Define output files for validation results
results_output = os.path.join(output_folder, f'{group}_results.csv')
importance_output = os.path.join(output_folder, f'{group}_importances.csv')
threshold_output_mean = os.path.join(output_folder, f'{group}_threshold_mean.txt')
auc_output = os.path.join(output_folder, f'{group}_auc.txt')
acc_output = os.path.join(output_folder, f'{group}_acc.txt')
rscore_output = os.path.join(output_folder, f'{group}_r2.txt')
rmse_output = os.path.join(output_folder, f'{group}_rmse.txt')
mae_output = os.path.join(output_folder, f'{group}_mae.txt')

# Define covariate sets
validation = ['valid']
predictor_clim = ['summer', 'january', 'precip']
predictor_s1 = ['s1_1_vha', 's1_1_vhd', 's1_1_vva', 's1_1_vvd',
                's1_2_vha', 's1_2_vhd', 's1_2_vva', 's1_2_vvd',
                's1_3_vha', 's1_3_vhd', 's1_3_vva', 's1_3_vvd']
predictor_s2 = [f's2_{i}_{band}' for i in range(1, 6) for band in
                ['blue', 'green', 'red', 'redge1', 'redge2', 'redge3', 'nir',
                 'redge4', 'swir1', 'swir2', 'nbr', 'ngrdi', 'ndmi', 'ndsi',
                 'ndvi', 'ndwi']]
predictor_topo = ['coast', 'stream', 'river', 'wetness',
                  'elevation', 'exposure', 'heatload', 'position',
                  'aspect', 'relief', 'roughness', 'slope']
predictor_emb = ['A' + str(i).zfill(2) for i in range(64)]

# Dynamically build predictor_all list from input arguments
predictor_map = {
    'clim': predictor_clim, 's1': predictor_s1, 's2': predictor_s2,
    'topo': predictor_topo, 'emb': predictor_emb
}
predictor_all = []
for name in predictor_names:
    if name in predictor_map:
        predictor_all.extend(predictor_map[name])
    else:
        print(f"Warning: Predictor set '{name}' not recognized and will be skipped.")
if not predictor_all:
    raise ValueError("No valid predictor sets were provided. Exiting.")

# Define other field sets
obs_pres = ['presence']
obs_cover = ['cover_percent']
retain_variables = ['site_visit_code'] + validation
all_variables = retain_variables + predictor_all + obs_pres + obs_cover
pred_abs = ['pred_abs']
pred_pres = ['pred_pres']
pred_bin = ['pred_bin']
pred_cover = ['pred_cover']
prediction = ['prediction']
outer_split = ['outer_split_n']
inner_split = ['inner_split_n']
inner_columns = all_variables + pred_abs + pred_pres + inner_split
outer_columns = all_variables + pred_abs + pred_pres + pred_cover + pred_bin + outer_split

# Define cross validation methods
outer_cv_splits = StratifiedGroupKFold(n_splits=10)
inner_cv_splits = StratifiedGroupKFold(n_splits=10)

#### PREPARE INPUT DATA
####____________________________________________________

# Read input data to data frames
print('Loading input data...')
start_time = time.time()
input_data = pd.read_csv(covariate_input).rename(
    columns={group: 'cover_percent'})

# Filter the input data to include valid data only
input_data = input_data[input_data['cover_percent'] >= 0].copy()

# Threshold the presence-absence data
input_data['presence'] = np.where(input_data['cover_percent'] >= presence_threshold, 1, 0)

# Shuffle data
shuffled_data = shuffle(input_data, random_state=314).copy()
end_timing(start_time)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# PART 1: TRAIN FINAL MODEL ON FULL DATASET
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Prepare Earth Engine
print('Requesting information from server...')
iteration_start = time.time()
ee.Authenticate()
ee.Initialize(project='akveg-map')
# Create a null geometry point. This is needed to properly export the feature collection
null_geometry = ee.Geometry.Point([0, 0])
end_timing(iteration_start)

# Train final classifier and export to Google Earth Engine asset
asset_id = f'projects/akveg-map/assets/models/foliar_cover/test_asset'

# Train classifier
classifier_params = {'n_estimators': 10,
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
                         'n_jobs': 1,
                         'random_state': 314}

# Split the X and y data for classification
X_classify = shuffled_data[predictor_all].astype(float)
y_classify = shuffled_data[obs_pres[0]].astype('int32')

# Train classifier
final_classifier = BalancedRandomForestClassifier(**classifier_params)
final_classifier.fit(X_classify, y_classify)

# Convert the classifier into a feature class
print('Converting decision trees to feature class...')
decision_trees = ml.rf_to_strings(final_classifier, predictor_all)

# Export trees to feature class
features = [
    ee.Feature(null_geometry, {"tree": tree.replace("\n", "#")}) for tree in decision_trees
]
tree_fc = ee.FeatureCollection(features)

    # Create and initiate export task
    print('Saving model as GEE asset...')
    task = ee.batch.Export.table.toAsset(
        collection=tree_fc,
        description=asset_name,
        assetId=asset_id
    )
    task.start()
    end_timing(iteration_start)

    # Increase count
    count += 1
