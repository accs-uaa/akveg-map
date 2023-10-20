# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic indices
# Author: Timm Nawrocki
# Last Updated: 2023-10-19
# Usage: Execute in ArcGIS Pro Python 3.9+.
# Description: "Calculate topographic indices" calculates a suite of topographic indices as new rasters from a DTM input raster.
# ---------------------------------------------------------------------------

# Import packages
import os
import time
from akutils import *
from geomorph import *

# Set parameter values
z_unit = 'METER'
position_width = 5000

# Set root directory
drive = 'D:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography/Alaska_Composite_DTM_10m')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
input_folder = os.path.join(data_folder, 'float')
output_folder = os.path.join(data_folder, 'integer')

# Define input files
elevation_float = os.path.join(input_folder, 'Elevation_10m_3338.tif')
area_file = os.path.join(drive, root_folder, 'Data/topography/area_test.tif')
#area_file = os.path.join(project_folder, 'Data_Input', 'AlaskaYukon_MapDomain_10m_3338.tif')

# Define output files
elevation_integer = os.path.join(output_folder, 'Elevation_10m_3338.tif')
slope_float = os.path.join(input_folder, 'Slope_10m_3338.tif')
slope_integer = os.path.join(output_folder, 'Slope_10m_3338.tif')
aspect_float = os.path.join(input_folder, 'Aspect_10m_3338.tif')
aspect_integer = os.path.join(output_folder, 'Aspect_10m_3338.tif')
linear_aspect = os.path.join(input_folder, 'LinearAspect_10m_3338.tif')
exposure_output = os.path.join(output_folder, 'Exposure_10m_3338.tif')
heatload_output = os.path.join(output_folder, 'HeatLoad_10m_3338.tif')
position_output = os.path.join(output_folder, 'Position_10m_3338.tif')
radiation_output = os.path.join(output_folder, 'RadiationAspect_10m_3338.tif')
roughness_output = os.path.join(output_folder, 'Roughness_10m_3338.tif')
ruggedness_output = os.path.join(output_folder, 'Ruggedness_10m_3338.tif')
surfacearea_output = os.path.join(output_folder, 'SurfaceArea_10m_3338.tif')
surfacerelief_output = os.path.join(output_folder, 'Relief_10m_3338.tif')
direction_float = os.path.join(input_folder, 'Direction_10m_3338.tif')
accumulation_float = os.path.join(input_folder, 'Accumulation_10m_3338.tif')
wetness_output = os.path.join(output_folder, 'Wetness_10m_3338_Weighted.tif')

#### CALCULATE FOUNDATIONAL TOPOGRAPHY DATASETS

# Calculate slope if it does not already exist
if os.path.exists(slope_float) == 0:
    print('Calculating slope...')
    iteration_start = time.time()
    calculate_slope(area_file, elevation_float, z_unit, slope_float, slope_integer)
    end_timing(iteration_start)
else:
    print('Slope already exists.')
    print('----------')

# Calculate aspect if it does not already exist
if os.path.exists(aspect_float) == 0:
    # Calculate aspect
    print('Calculating aspect...')
    iteration_start = time.time()
    calculate_aspect(area_file, elevation_float, z_unit, aspect_float, aspect_integer)
    end_timing(iteration_start)
else:
    print('Aspect already exists.')
    print('----------')

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

#### CALCULATE DERIVED INDICES

# Calculate solar exposure index if it does not already exist
if os.path.exists(exposure_output) == 0:
    print('Calculating solar exposure...')
    iteration_start = time.time()
    calculate_exposure(area_file, aspect_float, slope_float, 10, exposure_output)
    end_timing(iteration_start)
else:
    print('Solar exposure already exists.')
    print('----------')

# Calculate heat load index if it does not already exist
if os.path.exists(heatload_output) == 0:
    print('Calculating heat load index...')
    iteration_start = time.time()
    calculate_heat_load(area_file, elevation_float, slope_float, aspect_float, 10000, heatload_output)
    end_timing(iteration_start)
else:
    print('Heat load index already exists.')
    print('----------')

# Calculate topographic position if it does not already exist
if os.path.exists(position_output) == 0:
    print('Calculating topographic position...')
    iteration_start = time.time()
    calculate_position(area_file, elevation_float, position_width, position_output)
    end_timing(iteration_start)
else:
    print('Topographic position already exists.')
    print('----------')

# Calculate radiation aspect if it does not already exist
if os.path.exists(radiation_output) == 0:
    print('Calculating topographic radiation...')
    iteration_start = time.time()
    calculate_radiation_aspect(area_file, aspect_float, 1000, radiation_output)
    end_timing(iteration_start)
else:
    print('Topographic radiation already exists.')
    print('----------')

# Calculate roughness if it does not already exist
if os.path.exists(roughness_output) == 0:
    print('Calculating roughness...')
    iteration_start = time.time()
    calculate_roughness(area_file, elevation_float, 1, roughness_output)
    end_timing(iteration_start)
else:
    print('Roughness already exists.')
    print('----------')

# Calculate surface area ratio if it does not already exist
if os.path.exists(surfacearea_output) == 0:
    print('Calculating surface area ratio...')
    iteration_start = time.time()
    calculate_surface_area(area_file, slope_float, 10, surfacearea_output)
    end_timing(iteration_start)
else:
    print('Surface area ratio already exists.')
    print('----------')

# Calculate surface relief ratio if it does not already exist
if os.path.exists(surfacerelief_output) == 0:
    print('Calculating surface relief ratio...')
    iteration_start = time.time()
    calculate_surface_relief(area_file, elevation_float, 10000, surfacerelief_output)
    end_timing(iteration_start)
else:
    print('Surface relief ratio already exists.')
    print('----------')

# Calculate topographic wetness if it does not already exist
if os.path.exists(wetness_output) == 0:
    print('Calculating topographic wetness...')
    iteration_start = time.time()
    calculate_wetness(area_file, elevation_float, accumulation_float, 100, wetness_output)
    end_timing(iteration_start)
else:
    print('Topographic wetness already exists.')
    print('----------')
