# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Partition Model Validation Results by Region
# Author: Timm Nawrocki
# Last Updated: 2023-02-17
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Partition Model Validation Results by Region" extracts a set of predictor raster datasets to a study area to enforce the same extent on all rasters.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import partition_results

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/VegetationEcology/AKVEG_Map',
                           'Data/Data_Output/model_results/round_20230217/final')
region_geodatabase = os.path.join(drive,
                                  root_folder,
                                  'Projects/VegetationEcology/AKVEG_Map',
                                  'Data/archive/AKVEG_Regions.gdb')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_Map',
                                'Data/AKVEG_Workspace.gdb')

# Define regional feature classes
northern = os.path.join(region_geodatabase,
                        'NorthAmericanBeringia_Subregion_Northern')
western = os.path.join(region_geodatabase,
                       'NorthAmericanBeringia_Subregion_Western')
interior = os.path.join(region_geodatabase,
                        'NorthAmericanBeringia_Subregion_Interior')
regions = [northern, western, interior]

# Define model output folders
class_folders = ['alnus', 'betshr_nojan', 'bettre', 'dectre', 'dryas_nojan_noprec',
                 'empnig_nojan', 'erivag_noswi', 'picgla', 'picmar', 'rhoshr',
                 'salshr', 'sphagn', 'vaculi_nojan', 'vacvit', 'wetsed']

# Loop through model output folders and partition results for each region
count = 1
for class_folder in class_folders:
    # Define input folder
    input_folder = os.path.join(data_folder, class_folder)

    # Define input table
    input_table = os.path.join(input_folder, 'NorthAmericanBeringia_Region.csv')

    # Partition results to each region
    for region in regions:
        region_name = os.path.split(region)[1]
        print(f'Partitioning map class {count} of {len(class_folders)} for {region_name}...')

        # Define output table
        output_table = os.path.join(input_folder, region_name + '.csv')

        # Define input and output arrays
        partition_inputs = [region, input_table]
        partition_outputs = [output_table]

        # Create key word arguments
        partition_kwargs = {'work_geodatabase': work_geodatabase,
                            'input_projection': 3338,
                            'input_array': partition_inputs,
                            'output_array': partition_outputs
                            }

        # Extract raster to study area
        arcpy_geoprocessing(partition_results, **partition_kwargs)
        print('----------')

    # Increase counter
    count += 1
