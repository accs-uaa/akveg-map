import pandas as pd
import os
from sklearn.metrics import r2_score

directory = 'N:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/final'

input_file = os.path.join(directory,
                          'cladon_r2_0500_alag/prediction.csv')

projects = ['AIM GMT2', 'AIM NPR-A', 'Beringia VC', 'Bristol Bay VC', 'NPS Alagnak LC', 'NPS Alagnak ELS', 'NPS ARCN ELS', 'NPS Katmai ELS', 'NPS Lake Clark ELS', 'NPS Wrangell-St. Elias ELS', 'Selawik NWR ELS', 'Shell ONES Habitat', 'Dalton Earth Cover', 'Goodnews Earth Cover', 'Koyukuk Earth Cover', 'Kvichak Earth Cover', 'Naknek Earth Cover', 'Northern Yukon Earth Cover', 'Nowitna Earth Cover', 'Seward Peninsula Earth Cover', 'Southern Yukon Earth Cover', 'Tetlin Earth Cover', 'Yukon Delta Earth Cover']

input_data = pd.read_csv(input_file)

sw_data = input_data[(input_data['initialProject'] == 'Bristol Bay VC') |
                     (input_data['initialProject'] == 'NPS Alagnak LC') |
                     (input_data['initialProject'] == 'NPS Katmai ELS') |
                     (input_data['initialProject'] == 'NPS Lake Clark ELS') |
                     (input_data['initialProject'] == 'Naknek Earth Cover') |
                     (input_data['initialProject'] == 'Goodnews Earth Cover') |
                     (input_data['initialProject'] == 'Kvichak Earth Cover') |
                     (input_data['initialProject'] == 'Yukon Delta Earth Cover')]

y_regress_observed = sw_data['coverTotal']
y_regress_predicted = sw_data['prediction']

r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
print(f'Southwest Alaska: {r_score}')