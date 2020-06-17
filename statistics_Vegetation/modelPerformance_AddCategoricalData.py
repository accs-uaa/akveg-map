# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Add Categorical Map Data to Model Validation Results
# Author: Timm Nawrocki
# Created on: 2020-06-11
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Add Categorical Map Data to Model Validation Results" extracts categorical map classes to model validation results for the NLCD, the coarse classes of the Alaska Vegetation and Wetland Composite, and the fine classes of the Alaska Vegetation and Wetland Composite. This script also assigns the units for the 10x10 km and landscape scale accuracy assessments.
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
                           'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Output/model_results/final')
aux_folder = os.path.join(drive,
                          root_folder,
                          'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/auxiliary_data')
map_folder = os.path.join(drive,
                          root_folder,
                          'Data/biota/vegetation')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Define categorical maps
nlcd = os.path.join(map_folder, 'Alaska_NationalLandCoverDatabase_2011.img')
coarse = os.path.join(map_folder, 'AlaskaVegetationWetlandComposite_20180412_Coarse.tif')
fine = os.path.join(map_folder, 'AlaskaVegetationWetlandComposite_20180412_Fine.tif')
minor_grid = os.path.join(aux_folder, 'NorthAmericanBeringia_GridIndex_Minor_10km_Selected.tif')
ecoregions = os.path.join(aux_folder, 'NorthAmericanBeringia_UnifiedEcoregions.tif')
categorical_maps = [nlcd, coarse, fine, minor_grid, ecoregions]

# Define model output folders
class_folders = ['alnus_nmse', 'betshr_nmse', 'bettre_nmse', 'calcan_nmse', 'cladon_nmse', 'dectre_nmse', 'empnig_nmse', 'erivag_nmse', 'picgla_nmse', 'picmar_nmse', 'rhotom_nmse', 'salshr_nmse', 'sphagn_nmse', 'vaculi_nmse', 'vacvit_nmse', 'wetsed_nmse']

# Loop through model output folders and partition results for each region
count = 1
for class_folder in class_folders:
    print(f'Extracting categorical data for map class {count} of {len(class_folders)}...')

    # Define input folder
    input_folder = os.path.join(data_folder, class_folder)

    # Define input table
    input_table = os.path.join(input_folder, 'prediction.csv')

    # Define output table
    output_table = os.path.join(input_folder, 'mapRegion_Statewide.csv')

    # Define input and output arrays
    categorical_inputs = [input_table] + categorical_maps
    categorical_outputs = [output_table]

    # Create key word arguments
    categorical_kwargs = {'work_geodatabase': work_geodatabase,
                          'input_projection': 4269,
                          'input_array': categorical_inputs,
                          'output_array': categorical_outputs
                          }

    # Extract raster to study area
    arcpy_geoprocessing(extract_categorical_maps, **categorical_kwargs)
    print('----------')

    # Increase counter
    count += 1