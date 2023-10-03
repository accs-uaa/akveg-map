# Import packages for file manipulation, data manipulation, and plotting
import os
import numpy as np
import pandas as pd
# Import modules for preprocessing, model selection, linear regression, and performance from Scikit Learn
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

input_file = 'N:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/All_Data_Merged_Min.csv'
map_group = 'Picea_mariana'

input_data = pd.read_csv(input_file)
input_data['FIA_COVER'] = input_data['FIA_COVER'].astype(float)
input_data['MODEL_PREDICTED_COVER'] = input_data['MODEL_PREDICTED_COVER'].astype(float)

group_data = input_data[input_data.SPECIES_GRP == map_group].copy()
presence_data = group_data[group_data.FIA_COVER > 0]
cover_mean = presence_data['FIA_COVER'].mean()
cover_median = presence_data['FIA_COVER'].median()

y_regress_observed = group_data['FIA_COVER']
y_regress_predicted = group_data['MODEL_PREDICTED_COVER']

r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
mae = mean_absolute_error(y_regress_observed, y_regress_predicted)
rmse = np.sqrt(mean_squared_error(y_regress_observed, y_regress_predicted))

r_score
mae
rmse
cover_mean
cover_median