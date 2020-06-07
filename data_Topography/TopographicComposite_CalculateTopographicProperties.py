# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate Topographic Properties
# Author: Timm Nawrocki
# Last Updated: 2019-12-07
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Calculate Topographic Properties" creates a composite from multiple sources based on order of priority. All sources must be in the same projection with the same cell size and grid. The grid tiles must be predefined as rasters.
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
data_folder = os.path.join(drive, root_folder, 'Data/topography/Composite_10m_Beringia/gridded_full')

# Define input datasets
grid_major = os.path.join(drive, root_folder, 'Data/analyses/gridMajor')
snap_raster = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/Data_Input/northAmericanBeringia_TotalArea.tif')

# Define root input name
elevation_name_root = 'Elevation_Composite_10m_Beringia_AKALB_'

# Define root output names
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
# Set environment workspace to the folder containing the grid rasters
arcpy.env.workspace = grid_major
# Create a raster list using the Arcpy List Rasters function
raster_list = arcpy.ListRasters('*', 'TIF')
# Append file names to rasters in list
grids = []
for raster in raster_list:
    raster_path = os.path.join(grid_major, raster)
    grids.append(raster_path)
grids_length = len(grids)
print(f'Topographic properties will be calculated for {grids_length} grids...')
# End timing
iteration_end = time.time()
iteration_elapsed = int(iteration_end - iteration_start)
iteration_success_time = datetime.datetime.now()
# Report success
print(f'Completed at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
print('----------')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS/BeringiaVegetation.gdb')

# Iterate through each buffered grid and create elevation composite
for grid in grids:
    # Define composite raster name
    grid_title = os.path.splitext(os.path.split(grid)[1])[0]
    print(f'Calculating topographic properties for {grid_title}...')

    # Define input elevation dataset
    elevation = os.path.join(data_folder, grid_title, elevation_name_root + grid_title + '.tif')

    # Define output topographic datasets
    aspect = os.path.join(data_folder, grid_title, aspect_name_root + grid_title + '.tif')
    compoundTopographic = os.path.join(data_folder, grid_title, compoundTopographic_name_root + grid_title + '.tif')
    roughness = os.path.join(data_folder, grid_title, roughness_name_root + grid_title + '.tif')
    siteExposure = os.path.join(data_folder, grid_title, siteExposure_name_root + grid_title + '.tif')
    slope = os.path.join(data_folder, grid_title, slope_name_root + grid_title + '.tif')
    surfaceArea = os.path.join(data_folder, grid_title, surfaceArea_name_root + grid_title + '.tif')
    surfaceRelief = os.path.join(data_folder, grid_title, surfaceRelief_name_root + grid_title + '.tif')
    topographicPosition = os.path.join(data_folder, grid_title, topographicPosition_name_root + grid_title + '.tif')
    topographicRadiation = os.path.join(data_folder, grid_title, topographicRadiation_name_root + grid_title + '.tif')

    # Define input and output arrays
    topographic_inputs = [grid, elevation]
    topographic_outputs = [aspect,
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
