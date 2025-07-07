# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compare categorical map performance
# Author: Timm Nawrocki
# Last Updated: 2024-09-30
# Usage: Must be executed in an Anaconda Python 3.12+ installation.
# Description: "Compare categorical map performance" compares the performance of the foliar cover maps to that of categorical vegetation maps.
# ---------------------------------------------------------------------------

# Import packages
import numpy as np
import os
import pandas as pd
import rasterio
import time
from sklearn.preprocessing import OneHotEncoder
from sklearn.utils import shuffle
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from akutils import *

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set round date
round_date = 'round_20240930'

# Define species
group = 'wetsed'

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work/Projects/VegetationEcology/AKVEG_Map/Data'

# Define folder structure
landfire_folder = os.path.join(drive, 'ACCS_Work/Data/biota/vegetation/Alaska_Landfire_20')
species_folder = os.path.join(drive, root_folder, 'Data_Input/species_data')
output_folder = os.path.join(drive, root_folder, 'Data_Output/model_results', round_date, group)
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define input files
species_input = os.path.join(species_folder, f'cover_{group}_3338.csv')
landfire_input = os.path.join(landfire_folder, 'LF2023_EVT_240_AK/Tif/LA23_EVT_240.tif')

# Define variable sets
validation = ['valid']
retain_variables = ['st_vst', 'landfire'] + validation
obs_pres = ['presence']
obs_cover = ['cvr_pct']
pred_cover = ['pred_cover']
all_variables = retain_variables + obs_pres + obs_cover
outer_split = ['outer_split_n']
outer_columns = all_variables + pred_cover + outer_split

# Define cross validation methods
outer_cv_splits = StratifiedGroupKFold(n_splits=10)

#### PREPARE INPUT DATA
####____________________________________________________

# Read input data to data frame
print('Loading input data...')
iteration_start = time.time()
species_data = pd.read_csv(species_input)
species_data.index = range(len(species_data))
coords = [(x,y) for x, y in zip(species_data.cent_x, species_data.cent_y)]

# Open the raster and store metadata
landfire_raster = rasterio.open(landfire_input)

# Sample the raster at every point location and store values in DataFrame
species_data['landfire'] = [x[0] for x in landfire_raster.sample(coords)]

# Calculate mean and median value of presences
presence_data = species_data[species_data[obs_pres[0]] == 1]
cover_mean = presence_data[obs_cover[0]].mean()
cover_median = presence_data[obs_cover[0]].median()

# Remove no data values
input_data = species_data[species_data['landfire'] != -9999]
input_data = input_data[input_data[obs_cover[0]] >= 0].copy()

# Shuffle data
shuffled_data = shuffle(input_data, random_state=314)[all_variables].copy()

# Create an empty data frames to store results
outer_results = pd.DataFrame(columns=outer_columns)

#### CONDUCT MAP VALIDATION
####____________________________________________________

# Set the discrete X data
X_discrete = shuffled_data['landfire']

# Convert the X data to numpy array
X_discrete_array = np.asarray(X_discrete)
X_discrete_array = np.reshape(X_discrete_array, (-1, 1))

# Fit a one-hot encoder to the discrete map classes
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit(X_discrete_array)

# Transform X data using one-hot encoder
X_transformed_array = encoder.transform(X_discrete_array)

# Conduct outer cross validation iterations
outer_cv_i = 1
for train_index, test_index in outer_cv_splits.split(shuffled_data,
                                                     shuffled_data[obs_pres[0]].astype('int32'),
                                                     shuffled_data[validation[0]].astype('int32')):
    print(f'Conducting outer cross-validation iteration {outer_cv_i} of 10...')
    iteration_start = time.time()

    #### CONDUCT MODEL TRAIN
    ####____________________________________________________

    # Partition the outer train split by index
    train_iteration = shuffled_data.iloc[train_index]

    # Identify X and y train splits for the regressor
    X_regress_outer = X_transformed_array[train_index]
    y_regress_outer = train_iteration[obs_cover[0]].astype(float).copy()

    # Fit and predict a linear regression
    outer_regressor = LinearRegression()
    outer_regressor.fit(X_regress_outer, y_regress_outer)

    #### CONDUCT MODEL TEST
    ####____________________________________________________

    # Partition the outer test split by index
    outer_test_iteration = shuffled_data.iloc[test_index]

    # Identify X test split
    X_test_outer = X_transformed_array[test_index]

    # Use the regressor to predict foliar cover response
    cover_outer = outer_regressor.predict(X_test_outer)

    # Assign predicted values to outer test data frame
    outer_test_iteration = outer_test_iteration.assign(pred_cover=cover_outer)
    outer_test_iteration = outer_test_iteration.assign(outer_split_n=outer_cv_i)

    # Add the test results to output data frame
    outer_results = pd.concat([outer_results if not outer_results.empty else None,
                               outer_test_iteration],
                              axis=0)
    end_timing(iteration_start)

    # Increase iteration number
    outer_cv_i += 1

#### CALCULATE PERFORMANCE AND STORE RESULTS
####____________________________________________________

# Partition output results to foliar cover observed and predicted
y_regress_observed = outer_results[obs_cover[0]].astype(float).copy()
y_regress_predicted = outer_results[pred_cover[0]].astype(float).copy()

# Calculate performance metrics from output_results
r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

# Modify metrics for export
export_rscore = round(r_score, 3)
export_rmse = round(rmse, 1)
export_mae = round(mae, 1)

print(export_rscore)