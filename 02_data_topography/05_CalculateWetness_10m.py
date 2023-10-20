# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic indices
# Author: Timm Nawrocki
# Last Updated: 2023-10-09
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate topographic indices" calculates a suite of topographic indices as new rasters from a DTM input raster.
# ---------------------------------------------------------------------------

# Import packages
import os
import arcpy
from geomorph import calculate_flow
from geomorph import calculate_wetness

# Set parameter values
nodata = -32768

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
input_folder = os.path.join(data_folder, 'Alaska_Composite_DTM_10m/float')
output_folder = os.path.join(data_folder, 'Alaska_Composite_DTM_10m/integer')

# Define input files
elevation_float = os.path.join(input_folder, 'Elevation_10m_3338.tif')
area_file = os.path.join(data_folder, 'area_test.tif')
#area_file = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define output files
accumulation_float = os.path.join(input_folder, 'Accumulation_10m_3338.tif')
wetness_output = os.path.join(output_folder, 'Wetness_10m_3338.tif')

# Calculate flow accumulation if it does not already exist
if arcpy.Exists(accumulation_float) == 0:
    # Calculate flow direction
    print(f'\tCalculating flow direction...')
    calculate_flow(area_file, elevation_float, accumulation_float)
else:
    print(f'\tFlow direction already exists.')
    print('\t----------')

# Calculate topographic wetness if it does not already exist
if arcpy.Exists(wetness_output) == 0:
    print(f'\tCalculating topographic wetness...')
    calculate_wetness(area_file, elevation_float, flow_accumulation, slope_float, 100, wetness_output)
else:
    print(f'\tTopographic wetness already exists.')
    print('\t----------')
