# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Sentinel-1 composite
# Author: Timm Nawrocki
# Last Updated: 2021-11-20
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Sentinel-1 composite" merges Sentinel-1 tiles by month and property per predefined grid.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import glob
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import merge_spectral_tiles

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/imagery/sentinel-1')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/nab')
processed_folder = os.path.join(data_folder, 'processed/nab')
output_folder = os.path.join(data_folder, 'gridded/nab')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define input datasets
nab_raster = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

# Define property values
bands = ['vh', 'vv']

#### CREATE COMPOSITE DATA

# Iterate through each buffered grid and create spectral composite
for band in bands:
    # Create list of all metric tiles
    file_search = 'Sent1_' + band + '*.tif'
    metric_tiles = glob.glob(os.path.join(processed_folder, file_search))

    # Set initial count
    count = 1

    # For each grid, process the spectral metric
    for grid in grid_list:
        # Define folder structure
        output_path = os.path.join(output_folder, grid)
        output_raster = os.path.join(output_path, 'Sent1_' + band + '_' + grid + '.tif')

        # Make grid folder if it does not already exist
        if os.path.exists(output_path) == 0:
            os.mkdir(output_path)

        # Define the grid raster
        grid_raster = os.path.join(grid_folder, grid + '.tif')

        # If output raster does not exist then create output_raster
        if arcpy.Exists(output_raster) == 0:
            # Create key word arguments
            kwargs_merge = {'cell_size': 10,
                            'output_projection': 3338,
                            'work_geodatabase': work_geodatabase,
                            'input_array': [nab_raster, grid_raster] + metric_tiles,
                            'output_array': [output_raster]
                            }

            # Process the merge tiles function
            print(f'Processing {band} grid {count} of {len(grid_list)}...')
            arcpy_geoprocessing(merge_spectral_tiles, **kwargs_merge)
            print('----------')
        else:
            print(f'Spectral grid {count} of {len(grid_list)} for {band} already exists.')
            print('----------')

        # Increase counter
        count += 1
