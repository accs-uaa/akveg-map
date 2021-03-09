# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Topographic Properties
# Author: Timm Nawrocki
# Last Updated: 2021-02-25
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Calculate Topographic Properties" calculates integer versions of ten topographic indices for each grid using elevation float rasters.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import datetime
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_topographic_properties
import time

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = os.path.join(drive, root_folder, 'Data/topography/Composite_10m_Beringia')
data_input = os.path.join(data_folder, 'float/gridded_full')
data_output = os.path.join(data_folder, 'integer/gridded_full')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')

# Define root names
elevation_name_root = 'Elevation_Composite_10m_Beringia_AKALB_'
aspect_name_root = 'Aspect_Composite_10m_Beringia_AKALB_'
compoundTopographic_name_root = 'CompoundTopographic_Composite_10m_Beringia_AKALB_'
roughness_name_root = 'Roughness_Composite_10m_Beringia_AKALB_'
siteExposure_name_root = 'SiteExposure_Composite_10m_Beringia_AKALB_'
slope_name_root = 'MeanSlope_Composite_10m_Beringia_AKALB_'
surfaceArea_name_root = 'SurfaceArea_Composite_10m_Beringia_AKALB_'
surfaceRelief_name_root = 'SurfaceRelief_Composite_10m_Beringia_AKALB_'
topographicPosition_name_root = 'TopographicPosition_Composite_10m_Beringia_AKALB_'
topographicRadiation_name_root = 'TopographicRadiation_Composite_10m_Beringia_AKALB_'

# Set overwrite option
arcpy.env.overwriteOutput = True

# List grid rasters
print('Searching for grid rasters...')
# Start timing function
iteration_start = time.time()
# Create a list of included grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']
# Append file names to rasters in list
grids = []
for grid in grid_list:
    raster_path = os.path.join(grid_major, 'Grid_' + grid + '.tif')
    grids.append(raster_path)
grids_length = len(grids)
print(f'Topographic indices will be calculated for {grids_length} grids...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Iterate through each buffered grid and create elevation composite
for grid in grids:
    # Define composite raster name
    grid_title = os.path.splitext(os.path.split(grid)[1])[0]
    print(f'Calculating topographic properties for {grid_title}...')

    # Define input elevation dataset
    elevation_input = os.path.join(data_input, grid_title, elevation_name_root + grid_title + '.tif')

    # Define output topographic datasets
    elevation_output = os.path.join(data_output, grid_title, elevation_name_root + grid_title + '.tif')
    aspect = os.path.join(data_output, grid_title, aspect_name_root + grid_title + '.tif')
    compoundTopographic = os.path.join(data_output, grid_title, compoundTopographic_name_root + grid_title + '.tif')
    roughness = os.path.join(data_output, grid_title, roughness_name_root + grid_title + '.tif')
    siteExposure = os.path.join(data_output, grid_title, siteExposure_name_root + grid_title + '.tif')
    slope = os.path.join(data_output, grid_title, slope_name_root + grid_title + '.tif')
    surfaceArea = os.path.join(data_output, grid_title, surfaceArea_name_root + grid_title + '.tif')
    surfaceRelief = os.path.join(data_output, grid_title, surfaceRelief_name_root + grid_title + '.tif')
    topographicPosition = os.path.join(data_output, grid_title, topographicPosition_name_root + grid_title + '.tif')
    topographicRadiation = os.path.join(data_output, grid_title, topographicRadiation_name_root + grid_title + '.tif')

    # Define input and output arrays
    topographic_inputs = [grid, elevation_input]
    topographic_outputs = [elevation_output,
                           aspect,
                           compoundTopographic,
                           roughness,
                           siteExposure,
                           slope,
                           surfaceArea,
                           surfaceRelief,
                           topographicPosition,
                           topographicRadiation]

    # Create key word arguments
    topographic_kwargs = {'z_unit': 'METER',
                          'input_array': topographic_inputs,
                          'output_array': topographic_outputs
                          }

    # Process the topographic calculations
    arcpy_geoprocessing(calculate_topographic_properties, **topographic_kwargs, check_output=False)
    print('----------')
