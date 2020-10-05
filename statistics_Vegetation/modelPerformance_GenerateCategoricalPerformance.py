# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Generate Categorical Performance
# Author: Timm Nawrocki
# Last Updated: 2020-06-06
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Generate Categorical Performance" calculates the r squared, mean absolute error, and root mean squared error of the categorical vegetation maps.
# ---------------------------------------------------------------------------

# Import packages for file manipulation, data manipulation, and plotting
import os
import numpy as np
import pandas as pd
# Import modules for preprocessing, model selection, linear regression, and performance from Scikit Learn
from sklearn.preprocessing import OneHotEncoder
from sklearn.utils import shuffle
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
# Import timing packages
import time
import datetime

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/final')

# Define output csv file
categorical_csv = os.path.join(data_folder, 'performance_categorical.csv')

# Define model output folders
class_folders = ['alnus_nmse', 'betshr_nmse', 'bettre_nmse', 'calcan_nmse', 'cladon_nmse', 'dectre_nmse', 'empnig_nmse', 'erivag_nmse', 'picgla_nmse', 'picmar_nmse', 'rhotom_nmse', 'salshr_nmse', 'sphagn_nmse', 'vaculi_nmse', 'vacvit_nmse', 'wetsed_nmse']

# Define vegetation map variables and regions
vegetation_maps = [['nlcd'], ['coarse'], ['fine']]
regions = ['Statewide', 'Arctic', 'Southwest', 'Interior']

# Define output variables
output_variables = ['mapClass', 'region', 'vegMap', 'r2', 'std_mae']

# Create empty data frame
categorical_performance = pd.DataFrame(columns = output_variables)

# Define static variables
cover = ['coverTotal']
discrete_response = ['discrete_response']

# Define 10-fold cross validation split methods
outer_cv_splits = KFold(n_splits=10, shuffle=True, random_state=314)

# Loop through model output folders and calculate map performance
count = 1
for class_folder in class_folders:
    for region in regions:
        # Read input data file
        input_file = os.path.join(data_folder, class_folder, 'mapRegion_' + region + '.csv')
        input_data = pd.read_csv(input_file)
        # Convert values to floats
        input_data[cover[0]] = input_data[cover[0]].astype(float)

        # Subset cover data (relevant for Lichens only)
        input_data = input_data[input_data['initialProject'] != 'NPS ARCN Lichen']

        # Shuffle data
        input_data = shuffle(input_data, random_state=21)

        # Calculate mean and median value of presences
        presence_data = input_data[input_data['regress'] == 1]
        mean_cover = presence_data['coverTotal'].mean()

        # Loop through categorical maps
        for map in vegetation_maps:
            # Set the discrete X data
            X_discrete = input_data[map[0]]
            # Convert the X data to numpy array
            X_discrete_array = np.asarray(X_discrete)
            X_discrete_array = np.reshape(X_discrete_array, (-1, 1))

            # Fit a one-hot encoder to the discrete map classes
            encoder = OneHotEncoder(handle_unknown='ignore')
            encoder.fit(X_discrete_array)
            # Transform X data using one-hot encoder
            X_transformed_array = encoder.transform(X_discrete_array)

            # Create an empty data frame to store the outer test results
            outer_results = pd.DataFrame(columns=cover + map + discrete_response + ['iteration'])

            # Iterate through outer cross-validation splits
            i = 1
            for train_index, test_index in outer_cv_splits.split(input_data):
                #### CONDUCT MODEL TRAIN

                # Partition the outer train split by iteration number
                iteration_start = time.time()
                train_iteration = input_data.iloc[train_index]

                # Identify X and y train splits for the regressor
                X_train_regress = X_transformed_array[train_index]
                y_train_regress = train_iteration[cover[0]]

                # Fit and predict a linear regression
                regression = LinearRegression()
                regression.fit(X_train_regress, y_train_regress)

                #### CONDUCT MODEL TEST

                # Partition the outer test split by iteration number
                test_iteration = input_data.iloc[test_index]

                # Identify X test split
                X_test = X_transformed_array[test_index]

                # Use the regressor to predict foliar cover response
                response_prediction = regression.predict(X_test)
                # Concatenate predicted values to test data frame
                test_iteration = test_iteration.assign(discrete_response = response_prediction)

                # Add iteration number to test iteration
                test_iteration = test_iteration.assign(iteration = i)

                # Add the test results to output data frame
                outer_results = outer_results.append(test_iteration, ignore_index=True, sort=True)

                # Increase iteration number
                i += 1

            # Partition output results to foliar cover observed and predicted
            y_regress_observed = outer_results[cover[0]]
            y_regress_predicted = outer_results[discrete_response[0]]

            # Calculate performance metrics from output_results
            r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None,
                               multioutput='uniform_average')
            mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
            rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

            # Create row in performance data frame to store results
            iteration_results = pd.DataFrame([[class_folder,
                                               region,
                                               map[0],
                                               round(r_score, 2),
                                               round((mae / mean_cover), 2)
                                               ]],
                                             columns = output_variables)
            categorical_performance = categorical_performance.append(iteration_results, ignore_index=True)

# Export categorical performance to csv
categorical_performance.to_csv(categorical_csv, header=True, index=False, sep=',', encoding='utf-8')