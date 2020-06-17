# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Continuous Performance
# Author: Timm Nawrocki
# Created on: 2020-06-11
# Usage: Must be executed in an Anaconda Python 3.7 installation.
# Description: "Generate Continuous Performance" calculates the r squared, standardized mean absolute error, auc, and percentage distribution accuracy of the continuous vegetation maps at the native map resolution.
# ---------------------------------------------------------------------------

# Import packages for file manipulation, data manipulation, and plotting
import os
import numpy as np
import pandas as pd
# Import modules for preprocessing, model selection, linear regression, and performance from Scikit Learn
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/final')

# Define output csv file
continuous_csv = os.path.join(data_folder, 'performance_continuous.csv')

# Define model output folders
class_folders = ['alnus_nmse', 'betshr_nmse', 'bettre_nmse', 'calcan_nmse', 'cladon_nmse', 'dectre_nmse', 'empnig_nmse', 'erivag_nmse', 'picgla_nmse', 'picmar_nmse', 'rhotom_nmse', 'salshr_nmse', 'sphagn_nmse', 'vaculi_nmse', 'vacvit_nmse', 'wetsed_nmse']

# Define vegetation map variables and regions
regions = ['Statewide', 'Arctic', 'Southwest', 'Interior']

# Define output variables
output_variables = ['mapClass', 'region', 'vegMap', 'r2', 'std_mae', 'auc', 'acc']

# Create empty data frame
continuous_performance = pd.DataFrame(columns = output_variables)

# Define static variables
cover = ['coverTotal']
prediction = ['prediction']
zero_variable = ['zero']
distribution = ['distribution']
presence = ['presence']

# Loop through model output folders and calculate map performance
count = 1
for class_folder in class_folders:
    for region in regions:
        # Read input data file and subset cover data (relevant for Lichens only)
        input_file = os.path.join(data_folder, class_folder, 'mapRegion_' + region + '.csv')
        input_data = pd.read_csv(input_file)
        # Convert values to floats
        input_data[cover[0]] = input_data[cover[0]].astype(float)
        input_data[prediction[0]] = input_data[prediction[0]].astype(float)

        # Partition output results to presence-absence observed and predicted
        y_classify_observed = input_data[zero_variable[0]].astype('int32')
        y_classify_predicted = input_data[distribution[0]].astype('int32')
        y_classify_probability = input_data[presence[0]]

        # Determine error rates
        confusion_test = confusion_matrix(y_classify_observed, y_classify_predicted)
        true_negative = confusion_test[0, 0]
        false_negative = confusion_test[1, 0]
        true_positive = confusion_test[1, 1]
        false_positive = confusion_test[0, 1]
        # Calculate sensitivity and specificity
        sensitivity = true_positive / (true_positive + false_negative)
        specificity = true_negative / (true_negative + false_positive)
        # Calculate AUC score
        auc = roc_auc_score(y_classify_observed, y_classify_probability)
        # Calculate overall accuracy
        accuracy = (true_negative + true_positive) / (true_negative + false_positive + false_negative + true_positive)

        # Subset cover data (relevant for Lichens only)
        input_data = input_data[input_data['initialProject'] != 'NPS ARCN Lichen']

        # Calculate mean and median value of presences
        presence_data = input_data[input_data['regress'] == 1]
        mean_cover = presence_data['coverTotal'].mean()

        # Partition output results to foliar cover observed and predicted
        y_regress_observed = input_data[cover[0]]
        y_regress_predicted = input_data[prediction[0]]

        # Calculate performance metrics from output_results
        r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None,
                               multioutput='uniform_average')
        mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
        rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

        # Create row in performance data frame to store results
        region_results = pd.DataFrame([[class_folder,
                                        region,
                                        'continuous',
                                        round(r_score, 2),
                                        round((mae / mean_cover), 2),
                                        round(auc, 2),
                                        round(accuracy, 2)
                                        ]],
                                      columns = output_variables)
        continuous_performance = continuous_performance.append(region_results, ignore_index=True)

# Export categorical performance to csv
continuous_performance.to_csv(continuous_csv, header=True, index=False, sep=',', encoding='utf-8')