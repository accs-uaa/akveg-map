# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Validate imbalanced classifier
# Author: Timm Nawrocki
# Last Updated: 2024-07-31
# Usage: Must be executed in an Anaconda Python 3.12+ installation.
# Description: "Validate imbalanced classifier" validates a random forest classifier with random undersampling of the majority class. The model validation accounts for spatial autocorrelation by grouping in 100 km blocks.
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
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set round date
round_date = 'round_20240731_im'

# Define species
species = 'ARCUVA'
rare_list = ['CERALE', 'SAXALE', 'SAXCHE', 'SENPSE']

# Define cross validation methods
outer_cv_splits = StratifiedGroupKFold(n_splits=10)
inner_cv_splits = StratifiedGroupKFold(n_splits=10)

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/Botany/NPS_NorthPacificSteppingStones/Data')
extract_folder = os.path.join(project_folder, 'Data_Input/extract_data')
species_folder = os.path.join(project_folder, 'Data_Input/species_data')
output_folder = os.path.join(project_folder, 'Data_Output/model_results', round_date)

# Define input files
covariate_file = os.path.join(extract_folder, 'NPSS_Sites_Covariates_3338.csv')
# Define input file
species_file = os.path.join(species_folder, f'PresenceAbsence_{species}_3338.csv')

# Define output files
output_file = os.path.join(output_folder, f'{species}_Results.csv')
auc_file = os.path.join(output_folder, f'{species}_AUC.txt')
acc_file = os.path.join(output_folder, f'{species}_ACC.txt')
threshold_file = os.path.join(output_folder, f'{species}_Threshold.txt')
list_file = os.path.join(output_folder, f'{species}_ThresholdList.txt')

# Define variable sets
validation = ['valid']
region = ['region']
predictor_all = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A',
                 'NBR', 'NGRDI', 'NDMI', 'NDSI', 'NDVI', 'NDWI',
                 'summer', 'january', 'precip',
                 'coast', 'stream', 'river', 'wetness',
                 'elevation', 'exposure', 'heatload', 'position',
                 'aspect', 'relief', 'roughness', 'slope']
response = ['presence']
retain_variables = ['st_vst'] + validation + region
all_variables = retain_variables + predictor_all + response
outer_split = ['outer_split_n']
inner_split = ['inner_split_n']
absence = ['pred_abs']
presence = ['pred_pre']
prediction = ['pred_bin']
inner_columns = all_variables + absence + presence + inner_split
outer_columns = all_variables + absence + presence + prediction + outer_split

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
                     'n_jobs': 4,
                     'random_state': 314}

#### PREPARE INPUT DATA
####____________________________________________________

# Read input data to data frames
print('Loading input data...')
iteration_start = time.time()
covariate_data = pd.read_csv(covariate_file).drop(['valid'], axis=1)
species_data = pd.read_csv(species_file)[['st_vst', 'cvr_pct', 'presence', 'region', 'valid']]

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
                                                     shuffled_data[response[0]].astype('int32'),
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

    #### CONDUCT INNER CROSS VALIDATION
    ####____________________________________________________
    print('\tCreating inner cross validation splits...')
    # Partition the outer train split by iteration number
    outer_train_iteration = outer_train[outer_train[outer_split[0]] == outer_cv_i].copy()
    outer_test_iteration = outer_test[outer_test[outer_split[0]] == outer_cv_i].copy()

    # Create an empty data frame to store the inner cross validation splits
    inner_train = pd.DataFrame(columns=all_variables + inner_split)
    inner_test = pd.DataFrame(columns=all_variables + inner_split)

    # Create an empty data frame to store the inner test results
    inner_results = pd.DataFrame(columns=all_variables + absence + presence + ['inner_cv_split_n'])

    # Create inner cross validation splits
    count = 1
    for train_index, test_index in inner_cv_splits.split(outer_train_iteration,
                                                         outer_train_iteration[response[0]].astype('int32'),
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

    # Iterate through inner cross validation splits
    inner_cv_i = 1
    while inner_cv_i <= inner_cv_length:
        print(f'\tConducting inner cross validation iteration {inner_cv_i} of {inner_cv_length}...')
        inner_train_iteration = inner_train[inner_train[inner_split[0]] == inner_cv_i].copy()
        inner_test_iteration = inner_test[inner_test[inner_split[0]] == inner_cv_i].copy()

        # Identify X and y inner train and test splits
        X_train_inner = inner_train_iteration[predictor_all].astype(float).copy()
        y_train_inner = inner_train_iteration[response[0]].astype('int32').copy()
        X_test_inner = inner_test_iteration[predictor_all].astype(float).copy()

        # Train classifier on the inner train data
        inner_classifier = BalancedRandomForestClassifier(**classifier_params)
        inner_classifier.fit(X_train_inner, y_train_inner)

        # Predict probabilities for inner test data
        probability_inner = inner_classifier.predict_proba(X_test_inner)

        # Assign predicted values to inner test data frame
        inner_test_iteration = inner_test_iteration.assign(pred_abs=probability_inner[:, 0])
        inner_test_iteration = inner_test_iteration.assign(pred_pre=probability_inner[:, 1])

        # Add the test results to output data frame
        inner_results = pd.concat([inner_results if not inner_results.empty else None,
                                   inner_test_iteration],
                                  axis=0)

        # Increase n value
        inner_cv_i += 1

    #### CONDUCT INNER THRESHOLD DETERMINATION
    ####____________________________________________________

    # Limit results to model region
    print('\tOptimizing classification threshold...')
    region_inner_results = inner_results.loc[inner_results[region[0]] == 1]

    # Calculate the optimal threshold and performance of the presence-absence classification
    if species in rare_list:
        region_presence = len(
            region_inner_results.loc[
                (region_inner_results[response[0]] == 1) & (region_inner_results[region[0]] == 1)
            ]
        )
        x = int(region_presence * 0.2)
        threshold = x_wrong_threshold(region_inner_results, response, presence, x)
    else:
        threshold, sensitivity, specificity, auc, accuracy = determine_optimal_threshold(
            region_inner_results[presence[0]],
            region_inner_results[response[0]]
        )
    threshold_list.append(threshold)

    #### CONDUCT OUTER CROSS VALIDATION
    ####____________________________________________________

    # Identify X and y train splits for the classifier
    X_train_outer = outer_train_iteration[predictor_all].astype(float).copy()
    y_train_outer = outer_train_iteration[response[0]].astype('int32').copy()
    X_test_outer = outer_test_iteration[predictor_all].astype(float).copy()

    # Train classifier on the outer train data
    print('\tTraining outer classifier...')
    outer_classifier = BalancedRandomForestClassifier(**classifier_params)
    outer_classifier.fit(X_train_outer, y_train_outer)

    # Use the classifier to predict probability
    print('\tPredicting outer cross-validation test data...')
    probability_outer = outer_classifier.predict_proba(X_test_outer)

    # Assign predicted values to outer test data frame
    outer_test_iteration = outer_test_iteration.assign(pred_abs=probability_outer[:, 0])
    outer_test_iteration = outer_test_iteration.assign(pred_pre=probability_outer[:, 1])

    # Convert probability to presence-absence
    presence_zeros = np.zeros(outer_test_iteration[presence[0]].shape)
    presence_zeros[outer_test_iteration[presence[0]] >= threshold] = 1

    # Assign binary prediction values to test data frame
    outer_test_iteration = outer_test_iteration.assign(pred_bin=presence_zeros)

    # Add the test results to output data frame
    outer_results = pd.concat([outer_results if not outer_results.empty else None,
                               outer_test_iteration],
                              axis=0)
    end_timing(iteration_start)

    # Increase iteration number
    outer_cv_i += 1

#### CONDUCT OUTER THRESHOLD DETERMINATION
####____________________________________________________

# Limit results to model region
print('Optimizing classification threshold...')
region_outer_results = outer_results.loc[outer_results[region[0]] == 1]

# Calculate the optimal threshold and performance of the presence-absence classification
if species in rare_list:
    region_presence = len(
        region_outer_results.loc[
            (region_outer_results[response[0]] == 1) & (region_outer_results[region[0]] == 1)
        ]
    )
    x = int(region_presence * 0.2)
    threshold = x_wrong_threshold(region_outer_results, response, presence, x)
else:
    threshold, sensitivity, specificity, auc, accuracy = determine_optimal_threshold(
        region_outer_results[presence[0]],
        region_outer_results[response[0]]
    )

#### CALCULATE PERFORMANCE AND STORE RESULTS
####____________________________________________________

# Partition output results to presence-absence observed and predicted
y_classify_observed = region_outer_results[response[0]].astype('int32').copy()
y_classify_predicted = region_outer_results[prediction[0]].astype('int32').copy()
y_classify_probability = region_outer_results[presence[0]].astype(float).copy()

# Determine error rates
confusion_test = confusion_matrix(y_classify_observed, y_classify_predicted)
true_negative = confusion_test[0, 0]
false_negative = confusion_test[1, 0]
true_positive = confusion_test[1, 1]
false_positive = confusion_test[0, 1]

# Calculate metrics
validation_auc = roc_auc_score(y_classify_observed, y_classify_probability)
validation_accuracy = (true_negative + true_positive) / (true_negative + false_positive + false_negative + true_positive)

# Modify metrics for export
export_auc = round(validation_auc, 3)
export_accuracy = round(validation_accuracy * 100, 1)
export_threshold = round(threshold, 5)

# Store output results in csv file
print('Writing output files...')
iteration_start = time.time()
outer_results.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')
output_list = [auc_file, acc_file, threshold_file, list_file]
metric_list = [export_auc, export_accuracy, export_threshold, threshold_list]
count = 0
for metric in metric_list:
    output_file = output_list[count]
    file = open(output_file, 'w')
    file.write(str(metric))
    file.close()
    count += 1
end_timing(iteration_start)

# Print scores
print(export_auc)
print(export_accuracy)
print(export_threshold)
print(threshold_list)
print(np.mean(threshold_list))
