# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate hydrography datasets
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in an ArcGIS Pro Python 3.11+ installation.
# Description: "Calculate hydrography datasets" calculates topographic wetness index, distance from streams, and distance from rivers.
# ---------------------------------------------------------------------------

# Import packages
import glob
import os
import time
from akutils import *
from akgeomorph import calculate_wetness
from akgeomorph import calculate_flowline_distance

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
elevation_folder = os.path.join(drive, root_folder, 'Data/hydrography', 'tiles_elevation')
slope_folder = os.path.join(drive, root_folder, 'Data/hydrography', 'tiles_slope')
accumulation_folder = os.path.join(drive, root_folder, 'Data/hydrography', 'tiles_flow')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography', 'tiles_hydrography')

# Define input files
input_files = glob.glob(f'{elevation_folder}/*.tif')

#### CALCULATE HYDROGRAPHIC RASTERS
####____________________________________________________

# Calculate hydrography for each tile if it does not already exist
count = 1
for elevation_tile in input_files:
    # Define file name
    file_name = os.path.split(elevation_tile)[1]
    # Define input datasets
    accumulation_tile = os.path.join(accumulation_folder, file_name.replace('Elevation', 'Accumulation'))
    # Define output datasets
    slope_tile = os.path.join(slope_folder, file_name.replace('Elevation', 'Slope'))
    wetness_tile = os.path.join(hydrography_folder, file_name.replace('Elevation', 'Wetness'))
    stream_tile = os.path.join(hydrography_folder, file_name.replace('Elevation', 'Stream'))
    streamdist_tile = os.path.join(hydrography_folder, file_name.replace('Elevation', 'StreamDist'))
    river_tile = os.path.join(hydrography_folder, file_name.replace('Elevation', 'River'))
    riverdist_tile = os.path.join(hydrography_folder, file_name.replace('Elevation', 'RiverDist'))

    # Calculate topographic wetness with smoothing 3 if it does not already exist
    if os.path.exists(wetness_tile) == 0:
        print(f'Calculating wetness {count} of {len(input_files)}...')
        iteration_start = time.time()
        calculate_wetness(elevation_tile, accumulation_tile, 'METER', 100, 3, slope_tile, wetness_tile)
        end_timing(iteration_start)
    else:
        print(f'Wetness already exists for tile {count} of {len(input_files)}.')
        print('----------')

    # Calculate distance to streams if it does not already exist
    if os.path.exists(streamdist_tile) == 0:
        print(f'Calculating stream distance {count} of {len(input_files)}...')
        iteration_start = time.time()
        calculate_flowline_distance(accumulation_tile, 10000, stream_tile, streamdist_tile)
        end_timing(iteration_start)
    else:
        print(f'Stream distance already exists for tile {count} of {len(input_files)}.')
        print('----------')

    # Calculate distance to rivers if it does not already exist
    if os.path.exists(riverdist_tile) == 0:
        print(f'Calculating river distance {count} of {len(input_files)}...')
        iteration_start = time.time()
        calculate_flowline_distance(accumulation_tile, 1000000, river_tile, riverdist_tile)
        end_timing(iteration_start)
    else:
        print(f'River distance already exists for tile {count} of {len(input_files)}.')
        print('----------')

    # Increase count
    count += 1
