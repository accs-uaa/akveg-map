# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Partition Model Validation Results by Region
# Author: Timm Nawrocki
# Last Updated: 2020-11-30
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
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/Data_Output/model_results/final')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data/BeringiaVegetation.gdb')

# Define regional feature classes
arctic = os.path.join(work_geodatabase, 'mapRegion_Arctic')
southwest = os.path.join(work_geodatabase, 'mapRegion_Southwest')
interior = os.path.join(work_geodatabase, 'mapRegion_Interior')
regions = [arctic, southwest, interior]

# Define model output folders
class_folders = ['alnus_nmse', 'betshr_nmse', 'bettre_nmse', 'calcan_nmse', 'cladon_nmse', 'dectre_nmse', 'empnig_nmse', 'erivag_nmse', 'picgla_nmse', 'picmar_nmse', 'rhotom_nmse', 'salshr_nmse', 'sphagn_nmse', 'vaculi_nmse', 'vacvit_nmse', 'wetsed_nmse']

# Loop through model output folders and partition results for each region
count = 1
for class_folder in class_folders:
    # Define input folder
    input_folder = os.path.join(data_folder, class_folder)

    # Define input table
    input_table = os.path.join(input_folder, 'mapRegion_Statewide.csv')

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
                            'input_projection': 4269,
                            'input_array': partition_inputs,
                            'output_array': partition_outputs
                            }

        # Extract raster to study area
        arcpy_geoprocessing(partition_results, **partition_kwargs)
        print('----------')

    # Increase counter
    count += 1