# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert fire history to gridded burn year
# Author: Timm Nawrocki
# Last Updated: 2021-11-04
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Convert fire history to gridded burn year" converts the Fire History polygons from 2000-2021 to a raster with most recent burn year as the value per major grid.
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

# Define data folder structure
data_folder = os.path.join(drive, root_folder, 'Data/climatology/fire')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/nab')
output_folder = os.path.join(data_folder, 'gridded/nab')

# Define input datasets
fire_history = os.path.join(data_folder,
                            'unprocessed/AlaskaFireHistoryPerimeters_NWCG_AICC.gdb/AlaskaFireHistoryPerimeters_20201113')
study_area = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

# Define output datasets
recent_fire = os.path.join(data_folder,
                           'unprocessed/AlaskaFireHistoryPerimeters_NWCG_AICC.gdb/AlaskaFireHistoryPerimeters_1990_2021')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'BeringiaVegetation.gdb')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

#### FILTER FIRE HISTORY

# Create recent fire history polygon if it does not already exist
if arcpy.Exists(recent_fire) == 0:

    # Create key word arguments
    kwargs_recent = {'year_start': 1990,
                     'year_end': 2021,
                     'work_geodatabase': work_geodatabase,
                     'input_array': [fire_history],
                     'output_array': [recent_fire]
                     }

    # Filter fire history to year range
    print(f'Extracting fire perimeters for years 1990-2021...')
    arcpy_geoprocessing(recent_fire_history, **kwargs_recent)
    print('----------')
else:
    print(f'Recent fire history feature class already exists.')
    print('----------')

#### PARSE DATA TO GRIDS

# Set initial count
count = 1

# For each grid, process the climate metric
for grid in grid_list:
    # Define output folder and file
    output_path = os.path.join(output_folder, grid)
    output_raster = os.path.join(output_path, 'FireHistory_AKALB_' + grid + '.tif')

    # Make grid folder if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Define the grid raster
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # If output raster does not exist then create output raster
    if arcpy.Exists(output_raster) == 0:
        # Create key word arguments
        kwargs_grid = {'work_geodatabase': work_geodatabase,
                       'input_array': [recent_fire, study_area, grid_raster],
                       'output_array': [output_raster]
                       }

        # Extract raster to grid
        print(f'Processing grid {count} of {len(grid_list)}...')
        arcpy_geoprocessing(convert_fire_history, **kwargs_grid)
        print('----------')
    else:
        print(f'Grid {count} of {len(grid_list)} already exists.')
        print('----------')

    # Increase counter
    count += 1
