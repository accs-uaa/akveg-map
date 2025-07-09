# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add Categorical Map Data to Model Validation Results
# Author: Timm Nawrocki
# Last Updated: 2023-02-17
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Add Categorical Map Data to Model Validation Results" extracts categorical map classes to model validation results for the National Land Cover Database 2016, the coarse classes of the Alaska Vegetation and Wetland Composite, the fine classes of the Alaska Vegetation and Wetland Composite, the NASA ABoVE Land Cover map circa 2014, and the Landfire Existing Vegetation Classification 2016. This script also assigns the units for the 10x10 km and landscape scale accuracy assessments.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import extract_categorical_maps

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_Map',
                           'Data/Data_Output/model_results/round_20230217/final')
ancillary_folder = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_Map',
                                'Data/Data_Input/data_ancillary')
map_folder = os.path.join(drive,
                          root_folder,
                          'Data/biota/vegetation')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_Map',
                                'Data/AKVEG_Workspace.gdb')

# Define categorical maps
nlcd = os.path.join(map_folder,
                    'Alaska_NationalLandCoverDatabase/Alaska_NationalLandCoverDatabase_2016_20200213.img')
coarse = os.path.join(map_folder,
                      'Alaska_VegetationWetlandComposite/AlaskaVegetationWetlandComposite_20180412_Coarse.tif')
fine = os.path.join(map_folder,
                    'Alaska_VegetationWetlandComposite/AlaskaVegetationWetlandComposite_20180412_Fine.tif')
above = os.path.join(map_folder,
                     'NASA_ABoVE_AnnualLandcover/NorthAmericanBeringia_LandCover_ABoVE_2014.tif')
landfire = os.path.join(map_folder,
                        'Alaska_Landfire_20/LF2016_EVT_200_AK/Tif/LA16_EVT_200.tif')
epscor = os.path.join(map_folder,
                      'Epscor_Interior/Epscor_Vegetation_Interior.tif')
minor_grid = os.path.join(ancillary_folder,
                          'NorthAmericanBeringia_GridIndex_Minor_10km_Selected.tif')
ecoregions = os.path.join(ancillary_folder,
                          'NorthAmericanBeringia_UnifiedEcoregions.tif')
categorical_maps = [nlcd, coarse, fine, above, landfire, epscor, minor_grid, ecoregions]

# Define model output folders
class_folders = ['alnus', 'betshr_nojan', 'bettre', 'dectre', 'dryas_nojan_noprec',
                 'empnig_nojan', 'erivag_noswi', 'picgla', 'picmar', 'rhoshr',
                 'salshr', 'sphagn', 'vaculi_nojan', 'vacvit', 'wetsed']

# Loop through model output folders and partition results for each region
count = 1
for class_folder in class_folders:
    print(f'Extracting categorical data for map class {count} of {len(class_folders)}...')

    # Define input folder
    input_folder = os.path.join(data_folder, class_folder)

    # Define input table
    input_table = os.path.join(input_folder, 'prediction.csv')

    # Define output table
    output_table = os.path.join(input_folder, 'NorthAmericanBeringia_Region.csv')

    # Define input and output arrays
    categorical_inputs = [input_table] + categorical_maps
    categorical_outputs = [output_table]

    # Create key word arguments
    categorical_kwargs = {'work_geodatabase': work_geodatabase,
                          'input_projection': 3338,
                          'input_array': categorical_inputs,
                          'output_array': categorical_outputs
                          }

    # Extract raster to study area
    arcpy_geoprocessing(extract_categorical_maps, **categorical_kwargs)
    print('----------')

    # Increase counter
    count += 1
