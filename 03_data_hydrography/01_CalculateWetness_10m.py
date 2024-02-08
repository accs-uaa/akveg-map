# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate wetness indices
# Author: Timm Nawrocki
# Last Updated: 2023-10-21
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate wetness indices" calculates flow accumulation and wetness index.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
from akutils import *
from geomorph import *

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
topography_folder = os.path.join(drive, root_folder, 'Data/topography/Alaska_Composite_DTM_10m')
hydrography_folder = os.path.join(drive, root_folder, 'Data/hydrography')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define input files
elevation_float = os.path.join(topography_folder, 'float', 'Elevation_10m_3338.tif')
slope_float = os.path.join(topography_folder, 'float', 'Slope_10m_3338.tif')
area_file = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define output files
direction_float = os.path.join(hydrography_folder, 'intermediate', 'Direction_10m_3338.tif')
accumulation_float = os.path.join(hydrography_folder, 'intermediate', 'Accumulation_10m_3338.tif')
wetness_output = os.path.join(hydrography_folder, 'integer', 'Wetness_10m_3338.tif')

# Calculate flow accumulation if it does not already exist
if os.path.exists(accumulation_float) == 0:
    # Calculate flow direction
    print('Calculating flow direction...')
    iteration_start = time.time()
    calculate_flow(area_file, elevation_float, direction_float, accumulation_float)
    end_timing(iteration_start)
else:
    print('Flow direction already exists.')
    print('----------')

# Calculate topographic wetness with smoothing 3 if it does not already exist
if os.path.exists(wetness_output) == 0:
    print('Calculating topographic wetness (smoothing = 3)...')
    iteration_start = time.time()
    calculate_wetness(area_file, slope_float, accumulation_float, 100, 3, wetness_output)
    end_timing(iteration_start)
else:
    print('Topographic wetness (smoothing = 3) already exists.')
    print('----------')
