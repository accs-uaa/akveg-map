# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Scaled Performance
# Author: Timm Nawrocki
# Created on: 2020-11-30
# Usage: Must be executed in an Anaconda Python 3.7 installation.
# Description: "Generate Scaled Performance by Minor Grid" calculates the R squared and standardized mean absolute error of the continuous vegetation maps at the minor grid (10 x 10 km) resolution and the ecoregion scale.
# ---------------------------------------------------------------------------

# Import packages for file manipulation, data manipulation, and plotting
import os
import numpy as np
import pandas as pd
# Import modules for preprocessing, model selection, linear regression, and performance from Scikit Learn
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Output/model_results/final')

# Define output csv file
scaled_csv = os.path.join(data_folder, 'performance_scaled.csv')

# Define model output folders
class_folders = ['alnus_nmse', 'betshr_nmse', 'bettre_nmse', 'calcan_nmse', 'cladon_nmse', 'dectre_nmse', 'empnig_nmse', 'erivag_nmse', 'picgla_nmse', 'picmar_nmse', 'rhotom_nmse', 'salshr_nmse', 'sphagn_nmse', 'vaculi_nmse', 'vacvit_nmse', 'wetsed_nmse']

# Define scales
scales = ['grid', 'ecoregion']

# Define output variables
output_variables = ['mapClass', 'scale', 'vegMap', 'r2', 'std_mae']

# Create empty data frame
scaled_performance = pd.DataFrame(columns = output_variables)

# Define static variables
cover = ['coverTotal']
prediction = ['prediction']

# Loop through model output folders and calculate map performance
count = 1
for class_folder in class_folders:
    for scale in scales:
        # Read input data file and calculate mean cover
        input_file = os.path.join(data_folder, class_folder, 'mapRegion_Statewide.csv')
        input_data = pd.read_csv(input_file)
        # Convert values to floats
        input_data[cover[0]] = input_data[cover[0]].astype(float)
        # Calculate mean and median value of presences
        presence_data = input_data[input_data['regress'] == 1]
        mean_cover = presence_data['coverTotal'].mean()

        # Read scaled input data file
        scaled_file = os.path.join(data_folder, class_folder, 'scaledData_' + scale + '.csv')
        scaled_data = pd.read_csv(scaled_file)
        # Convert values to floats
        scaled_data[cover[0]] = scaled_data[cover[0]].astype(float)
        scaled_data[prediction[0]] = scaled_data[prediction[0]].astype(float)

        # Partition output results to foliar cover observed and predicted
        y_regress_observed = scaled_data[cover[0]]
        y_regress_predicted = scaled_data[prediction[0]]

        # Calculate performance metrics from output_results
        r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None,
                           multioutput='uniform_average')
        mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
        rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

        # Create row in performance data frame to store results
        scaled_results = pd.DataFrame([[class_folder,
                                       scale,
                                       'continuous',
                                       round(r_score, 2),
                                       round((mae / mean_cover), 2)
                                       ]],
                                     columns = output_variables)
        scaled_performance = scaled_performance.append(scaled_results, ignore_index=True)

# Export categorical performance to csv
scaled_performance.to_csv(scaled_csv, header=True, index=False, sep=',', encoding='utf-8')