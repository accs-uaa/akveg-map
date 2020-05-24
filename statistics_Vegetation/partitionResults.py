import pandas as pd
import os
from sklearn.metrics import r2_score

directory = 'N:/ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/iteration_10_all'

input_file = os.path.join(directory,
                          'betshr2/prediction.csv')

projects = ['AIM GMT2', 'AIM NPR-A', 'Bristol Bay VC', 'NPS Alagnak ELS', 'NPS Alagnak LC', 'NPS Aniakchak ELS', 'NPS Aniakchak LC', 'NPS ARCN ELS', 'NPS Katmai ELS', 'NPS Katmai LC', 'NPS Lake Clark ELS', 'NPS Wrangell-St. Elias ELS', 'NSSI LC', 'Selawik NWR ELS', 'Shell ONES Habitat']

input_data = pd.read_csv(input_file)
cover_data = input_data[(input_data['coverType'] == 'Quantitative') | (input_data['coverType'] == 'Semi-quantitative')]

for project in projects:
    project_data = cover_data[cover_data['initialProject'] == project]

    # Partition output results to foliar cover observed and predicted
    y_regress_observed = project_data['coverTotal']
    y_regress_predicted = project_data['prediction']

    try:
        r_score = r2_score(y_regress_observed, y_regress_predicted, sample_weight=None, multioutput='uniform_average')
    except:
        r_score = 'N/A'
    print(f'{project}: {r_score}')
