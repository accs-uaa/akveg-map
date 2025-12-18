# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate flow accumulation
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in an ArcGIS Pro Python 3.11+ installation.
# Description: "Calculate flow accumulation" calculates flow accumulation for all tiles in a folder.
# ---------------------------------------------------------------------------

# Import packages
import os
import glob
import time
from akutils import *
from akgeomorph import calculate_flow

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
tile_folder = os.path.join(hydrography_folder, 'tiles_elevation')
output_folder = os.path.join(hydrography_folder, 'tiles_flow')
if os.path.exists(output_folder) == 0:
    os.mkdir(output_folder)

# Define input files
input_files = glob.glob(f'{tile_folder}/*.tif')

#### CALCULATE FLOW ACCUMULATION
####____________________________________________________

# Calculate flow accumulation for each tile if it does not already exist
count = 1
for elevation_tile in input_files:
    # Define output files
    file_name = os.path.split(elevation_tile)[1]
    accumulation_tile = os.path.join(output_folder, file_name.replace('Elevation', 'Accumulation'))
    direction_tile = os.path.join(output_folder, file_name.replace('Elevation', 'Direction'))
    if os.path.exists(accumulation_tile) == 0:
        # Calculate flow direction
        print(f'Calculating flow accumulation {count} of {len(input_files)}...')
        iteration_start = time.time()
        calculate_flow(elevation_tile, accumulation_tile, direction_tile)
        end_timing(iteration_start)
    else:
        print(f'Flow direction already exists for tile {count} of {len(input_files)}.')
        print('----------')
    # Increase count
    count += 1
