# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Continuous Performance
# Author: Timm Nawrocki
# Last Updated: 2021-10-12
# Usage: Must be executed in an Anaconda Python 3.7+ installation.
# Description: "Generate Continuous Performance" calculates the r squared, mean absolute error, root mean squared error, auc, percentage distribution accuracy, mean cover, and median cover of the continuous vegetation maps at the native map resolution.
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
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap',
                           'Data/Data_Output/model_results/round_20211012/final')

# Define output csv file
continuous_csv = os.path.join(data_folder, 'performance_continuous.csv')

# Define model output folders
class_folders = ['alnus', 'betshr_nojan', 'bettre', 'dectre', 'dryas_nojan_noprec',
                 'empnig_nojan', 'erivag_noswi', 'picgla', 'picmar', 'rhoshr',
                 'salshr', 'sphagn', 'vaculi_nojan', 'vacvit', 'wetsed']

# Define vegetation map variables and regions
regions = ['Region',
           'Subregion_Northern',
           'Subregion_Western',
           'Subregion_Interior']

# Define output variables
output_variables = ['mapClass', 'region', 'vegMap', 'r2', 'mae', 'rmse',
                    'auc', 'acc', 'cover_mean', 'cover_median']

# Create empty data frame
continuous_performance = pd.DataFrame(columns=output_variables)

# Define static variables
cover = ['cover']
prediction = ['prediction']
zero_variable = ['zero']
distribution = ['distribution']
presence = ['presence']

# Loop through model output folders and calculate map performance
count = 1
for class_folder in class_folders:
    for region in regions:
        # Read input data file
        input_file = os.path.join(data_folder, class_folder, 'NorthAmericanBeringia_' + region + '.csv')
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

        # Calculate mean and median value of presences
        presence_data = input_data[input_data['zero'] == 1]
        cover_mean = presence_data['cover'].mean()
        cover_median = presence_data['cover'].median()

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
                                        round(mae, 2),
                                        round(rmse, 2),
                                        round(auc, 2),
                                        round(accuracy, 2),
                                        round(cover_mean, 2),
                                        round(cover_median, 2)
                                        ]],
                                      columns=output_variables)
        continuous_performance = continuous_performance.append(region_results, ignore_index=True)

# Export categorical performance to csv
continuous_performance.to_csv(continuous_csv, header=True, index=False, sep=',', encoding='utf-8')
