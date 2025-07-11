# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate performance table
# Author: Timm Nawrocki
# Last Updated: 2025-07-10
# Usage: Must be executed in an Anaconda Python 3.7+ installation.
# Description: "Calculate performance table" calculates a table of performance metrics at the site scale and landscape scale for all mapped indicators.
# ---------------------------------------------------------------------------

# Import packages for file manipulation, data manipulation, and plotting
import os
import numpy as np
import pandas as pd
# Import modules for preprocessing, model selection, linear regression, and performance from Scikit Learn
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

# Set round date
round_date = 'round_20241124'

# Set root directory
drive = 'C:/'
root_folder = 'ACCS_Work'

# Define file structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_Map',
                           'Data/Data_Output/model_results', round_date)

# Define output data
performance_output = os.path.join(data_folder, 'performance_table.csv')

# Define pre-determined field values
indicators = ['alnus', 'betshr', 'bettre', 'brotre', 'dryas', 'dsalix', 'empnig', 'erivag', 'mwcalama',
              'ndsalix', 'nerishr', 'picgla', 'picmar', 'picsit', 'poptre', 'populbt', 'rhoshr', 'rubspe',
              'sphagn', 'tsumer', 'vaculi', 'vacvit', 'wetsed']
names = ['alder shrubs',
         'birch shrubs',
         'birch trees',
         'broadleaf trees',
         'Dryas dwarf shrubs',
         'willow dwarf shrubs',
         'Empetrum nigrum',
         'Eriophorum vaginatum',
         'mesic-wet Calamagrostis',
         'willow non-dwarf shrubs',
         'needleleaf ericaceous dwarf shrubs',
         'white spruce',
         'black spruce',
         'Sitka spruce',
         'aspen',
         'poplar',
         'Rhododendron shrubs',
         'salmonberry',
         'Sphagnum moss',
         'mountain hemlock',
         'bog blueberry',
         'lingonberry',
         'wetland sedges']
model_types = ['lgbm', 'lgbm', 'lgbm', 'lgbm', 'lgbm no_clim', 'lgbm no_clim', 'lgbm no_clim',
               'lgbm', 'lgbm', 'lgbm', 'lgbm no_clim', 'lgbm', 'lgbm', 'rf', 'lgbm no_clim',
               'lgbm', 'lgbm', 'rf', 'lgbm', 'lgbm no_clim', 'lgbm', 'rf', 'lgbm']
life_forms = ['shrub', 'shrub', 'tree', 'tree', 'dwarf shrub', 'dwarf shrub', 'dwarf shrub',
              'herbaceous', 'herbaceous', 'shrub', 'dwarf shrub', 'tree', 'tree', 'tree',
              'tree', 'tree', 'dwarf shrub', 'shrub', 'moss', 'tree', 'shrub', 'dwarf shrub',
              'herbaceous']

# Define output variables
output_variables = ['abbrev', 'indicator_name', 'model_type', 'life_form', 'n_presence', 'r2_site', 'rmse_site',
                    'auc_site', 'acc_site', 'cover_median', 'cover_mean', 'r2_scaled', 'rmse_scaled', 'n_grid']

# Create empty data frame to store results
performance_data = pd.DataFrame(columns=output_variables)

# Loop through model output folders and calculate map performance
count = 1
for indicator in indicators:
    print(f'Processing performance data for indicator {count} of {len(indicators)}...')
    # Define indicator folder
    indicator_folder = os.path.join(data_folder, indicator)

    # Define input files
    r2_input = os.path.join(indicator_folder, indicator + '_r2.txt')
    rmse_input = os.path.join(indicator_folder, indicator + '_rmse.txt')
    auc_input = os.path.join(indicator_folder, indicator + '_auc.txt')
    acc_input = os.path.join(indicator_folder, indicator + '_acc.txt')
    site_input = os.path.join(indicator_folder, indicator + '_results.csv')
    scaled_input = os.path.join(indicator_folder, indicator + '_scaled.csv')

    # Read input data
    site_data = pd.read_csv(site_input)
    scaled_data = pd.read_csv(scaled_input)

    # Convert values to floats
    site_data['cvr_pct'] = site_data['cvr_pct'].astype(float)
    site_data['prediction'] = site_data['prediction'].astype(float)
    scaled_data['mean_cvr_pct'] = scaled_data['mean_cvr_pct'].astype(float)
    scaled_data['mean_prediction'] = scaled_data['mean_prediction'].astype(float)

    # Read performance metrics
    with open(r2_input, 'r') as text_read:
        r2_site = float(text_read.readline())
    with open(rmse_input, 'r') as text_read:
        rmse_site = float(text_read.readline())
    with open(auc_input, 'r') as text_read:
        auc_site = float(text_read.readline())
    with open(acc_input, 'r') as text_read:
        acc_site = float(text_read.readline())

    # Calculate mean and median cover for presences
    site_presences = site_data[site_data['cvr_pct'] >= 3]
    n_presence = len(site_presences)
    cover_mean = round(site_presences['cvr_pct'].mean(), 1)
    cover_median = round(site_presences['cvr_pct'].median(), 1)

    # Calculate scaled performance
    y_regress_observed = scaled_data['mean_cvr_pct'].astype(float)
    y_regress_predicted = scaled_data['mean_prediction'].astype(float)

    # Calculate performance metrics from output_results
    r2_scaled = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None,
                         multioutput='uniform_average')
    rmse_scaled = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))
    n_grid = len(scaled_data[scaled_data['mean_cvr_pct'] >= 1])

    # Create row in performance data frame to store results
    indicator_results = pd.DataFrame([[indicator,
                                       names[count - 1],
                                       model_types[count - 1],
                                       life_forms[count - 1],
                                       n_presence,
                                       r2_site,
                                       rmse_site,
                                       auc_site,
                                       acc_site,
                                       cover_median,
                                       cover_mean,
                                       round(r2_scaled, 3),
                                       round(rmse_scaled, 1),
                                       n_grid]],
                                     columns=output_variables)
    performance_data = pd.concat([performance_data if not performance_data.empty else None,
                                  indicator_results],
                                 axis=0)

    # Increase count
    count += 1
    print('----------')

# Export categorical performance to csv
print('Exporting data to csv...')
performance_data.to_csv(performance_output, header=True, index=False, sep=',', encoding='utf-8')
print('----------')
