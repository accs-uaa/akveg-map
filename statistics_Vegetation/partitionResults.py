import pandas as pd
import os
from sklearn.metrics import r2_score

directory = 'N:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/iteration_10_aer'

input_file = os.path.join(directory,
                          'calcan/prediction.csv')

projects = ['AIM GMT2', 'AIM NPR-A', 'Bristol Bay VC', 'NPS Alagnak LC', 'NPS ARCN ELS', 'NPS Katmai ELS', 'NPS Lake Clark ELS', 'NPS Wrangell-St. Elias ELS', 'Selawik NWR ELS', 'Shell ONES Habitat', 'Bering LC', 'Dalton Earth Cover', 'Goodnews Earth Cover', 'Koyukuk Earth Cover', 'Kvichak Earth Cover', 'Naknek Earth Cover', 'Northern Yukon Earth Cover', 'Nowitna Earth Cover', 'Seward Peninsula Earth Cover', 'Southern Yukon Earth Cover', 'Tetlin Earth Cover', 'Yukon Delta Earth Cover']

input_data = pd.read_csv(input_file)

y_regress_observed = input_data['coverTotal']
y_regress_predicted = input_data['prediction']

r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
print(f'Overall: {r_score}')

for project in projects:
    project_data = input_data[input_data['initialProject'] == project]
    project_data = project_data.reset_index(drop=True)

    # Partition output results to foliar cover observed and predicted
    y_regress_observed = project_data['coverTotal']
    y_regress_predicted = project_data['prediction']

    try:
        r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
        print(f'{project}: {round(r_score, 2)}')
    except:
        r_score = 'N/A'
        print(f'{project}: {r_score}')

bb_data = input_data[(input_data['initialProject'] == 'Bristol Bay VC') |
                     (input_data['initialProject'] == 'NPS Alagnak LC') |
                     (input_data['initialProject'] == 'Naknek Earth Cover') |
                     (input_data['initialProject'] == 'Goodnews Earth Cover') |
                     (input_data['initialProject'] == 'Kvichak Earth Cover') |
                     (input_data['initialProject'] == 'Yukon Delta Earth Cover')]

y_regress_observed = project_data['coverTotal']
y_regress_predicted = project_data['prediction']

r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
print(f'Bristol Bay: {r_score}')