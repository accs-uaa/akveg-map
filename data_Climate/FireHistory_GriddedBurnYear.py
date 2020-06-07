# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert Fire History To Gridded Burn Year
# Author: Timm Nawrocki
# Last Updated: 2020-06-02
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Convert Fire History To Gridded Burn Year" converts the Fire History polygons from 2000-2019 to a raster with most recent burn year as the value per major grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import convert_fire_history
from package_GeospatialProcessing import recent_fire_history

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data')

# Define data folder structure
input_fire = os.path.join(data_folder, 'Climatology/Fire')
input_grids = os.path.join(data_folder, 'analyses/GridMajor')

# Define input datasets
fire_history = os.path.join(input_fire, 'AlaskaFireHistory_Polygons.gdb/fire_location_polygons')

# Define intermediate datasets
recent_fire = os.path.join(input_fire, 'AlaskaFireHistory_Polygons.gdb/FirePerimeters_2000_2019')

# Define work environment
work_geodatabase = os.path.join(drive,
                                root_folder,
                                'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Identify target major grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6']

# Define input datasets
study_area = os.path.join(drive,
                          root_folder,
                          'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_ModelArea.tif')

# Create recent fire history polygon if it does not already exist
if arcpy.Exists(recent_fire) == 0:
    # Define input and output arrays
    recent_inputs = [fire_history]
    recent_outputs = [recent_fire]

    # Create key word arguments
    recent_kwargs = {'work_geodatabase': work_geodatabase,
                     'input_array': recent_inputs,
                     'output_array': recent_outputs
                     }

    # Extract raster to study area
    print(f'Extracting fire perimeters for years 2000-2019...')
    arcpy_geoprocessing(recent_fire_history, **recent_kwargs)
    print('----------')
else:
    print(f'Recent fire history feature class already exists.')
    print('----------')

# Loop through each grid in list and extract all predictors to study area
for grid in grid_list:

    # Define the grid raster
    grid_raster = os.path.join(input_grids, "Grid_" + grid + ".tif")

    # Define output raster and path
    output_path = os.path.join(input_fire, 'gridded_select', 'Grid_' + grid)
    output_raster = os.path.join(output_path, 'FireHistory_AKALB_Grid_' + grid + '.tif')
    # Make output directory if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Check if output already exists
    if arcpy.Exists(output_raster) == 0:
        # Define input and output arrays
        extract_inputs = [recent_fire, study_area, grid_raster]
        extract_outputs = [output_raster]

        # Create key word arguments
        extract_kwargs = {'work_geodatabase': work_geodatabase,
                          'input_array': extract_inputs,
                          'output_array': extract_outputs
                          }

        # Extract raster to study area
        print(f'Extracting fire history raster for Grid {grid}...')
        arcpy_geoprocessing(convert_fire_history, **extract_kwargs)
        print('----------')
    else:
        print(f'Fire history raster for Grid {grid} already exists.')
        print('----------')