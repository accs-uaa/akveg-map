# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic indices
# Author: Timm Nawrocki
# Last Updated: 2025-12-16
# Usage: Must be executed in an ArcGIS Pro Python 3.11+ installation.
# Description: "Calculate topographic indices" calculates a suite of topographic indices as new rasters from a DTM input raster.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
from akutils import *
from akgeomorph import *

# Set parameter values
z_unit = 'METER'
position_width = 5000

#### SET UP DIRECTORIES, FILES, AND FIELDS
####____________________________________________________

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
topography_folder = os.path.join(drive, root_folder, 'Data/topography/Alaska_Composite_DTM_10m')
input_folder = os.path.join(topography_folder, 'float')
output_folder = os.path.join(topography_folder, 'integer')

# Define input files
area_input = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')
elevation_input = os.path.join(input_folder, 'Elevation_10m_3338.tif')

# Define output files
elevation_output = os.path.join(output_folder, 'Elevation_10m_3338.tif')
slope_float = os.path.join(input_folder, 'Slope_10m_3338.tif')
slope_output = os.path.join(output_folder, 'Slope_10m_3338.tif')
aspect_float = os.path.join(input_folder, 'Aspect_10m_3338.tif')
aspect_output = os.path.join(input_folder, 'LinearAspect_10m_3338.tif')
exposure_output = os.path.join(output_folder, 'Exposure_10m_3338.tif')
heatload_output = os.path.join(output_folder, 'HeatLoad_10m_3338.tif')
position_output = os.path.join(output_folder, 'Position_10m_3338.tif')
radiation_output = os.path.join(output_folder, 'RadiationAspect_10m_3338.tif')
roughness_output = os.path.join(output_folder, 'Roughness_10m_3338.tif')
surfacerelief_output = os.path.join(output_folder, 'Relief_10m_3338.tif')

#### CALCULATE FOUNDATIONAL TOPOGRAPHY DATASETS
####____________________________________________________

# Calculate integer elevation if it does not already exist
if os.path.exists(elevation_output) == 0:
    print('Calculating integer elevation...')
    iteration_start = time.time()
    calculate_integer_elevation(area_input, elevation_input, elevation_output)
    end_timing(iteration_start)
else:
    print('Integer elevation already exists.')
    print('----------')

# Calculate slope if it does not already exist
if os.path.exists(slope_output) == 0:
    print('Calculating slope...')
    iteration_start = time.time()
    calculate_slope(area_input, elevation_input, z_unit, slope_float, slope_output)
    end_timing(iteration_start)
else:
    print('Slope already exists.')
    print('----------')

# Calculate aspect if it does not already exist
if os.path.exists(aspect_float) == 0:
    # Calculate aspect
    print('Calculating aspect...')
    iteration_start = time.time()
    calculate_aspect(area_input, elevation_input, z_unit, aspect_float, None)
    end_timing(iteration_start)
else:
    print('Aspect already exists.')
    print('----------')

#### CALCULATE DERIVED INDICES
####____________________________________________________

# Calculate solar exposure index if it does not already exist
if os.path.exists(exposure_output) == 0:
    print('Calculating solar exposure...')
    iteration_start = time.time()
    calculate_exposure(area_input, aspect_float, slope_float, 10, exposure_output)
    end_timing(iteration_start)
else:
    print('Solar exposure already exists.')
    print('----------')

# Calculate heat load index if it does not already exist
if os.path.exists(heatload_output) == 0:
    print('Calculating heat load index...')
    iteration_start = time.time()
    calculate_heat_load(area_input, elevation_input, slope_float, aspect_float, 10000, heatload_output)
    end_timing(iteration_start)
else:
    print('Heat load index already exists.')
    print('----------')

# Calculate topographic position if it does not already exist
if os.path.exists(position_output) == 0:
    print('Calculating topographic position...')
    iteration_start = time.time()
    calculate_position(area_input, elevation_input, position_width, position_output)
    end_timing(iteration_start)
else:
    print('Topographic position already exists.')
    print('----------')

# Calculate radiation aspect if it does not already exist
if os.path.exists(radiation_output) == 0:
    print('Calculating topographic radiation...')
    iteration_start = time.time()
    calculate_radiation_aspect(area_input, aspect_float, 1000, radiation_output)
    end_timing(iteration_start)
else:
    print('Topographic radiation already exists.')
    print('----------')

# Calculate roughness if it does not already exist
if os.path.exists(roughness_output) == 0:
    print('Calculating roughness...')
    iteration_start = time.time()
    calculate_roughness(area_input, elevation_input, 1, roughness_output)
    end_timing(iteration_start)
else:
    print('Roughness already exists.')
    print('----------')

# Calculate surface relief ratio if it does not already exist
if os.path.exists(surfacerelief_output) == 0:
    print('Calculating surface relief ratio...')
    iteration_start = time.time()
    calculate_surface_relief(area_input, elevation_input, 10000, surfacerelief_output)
    end_timing(iteration_start)
else:
    print('Surface relief ratio already exists.')
    print('----------')
