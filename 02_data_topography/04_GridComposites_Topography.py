# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic properties
# Author: Timm Nawrocki
# Last Updated: 2022-01-02
# Usage: Must be executed in an ArcGIS Pro Python 3.7 installation.
# Description: "Calculate topographic properties" calculates integer versions of ten topographic indices for each grid using elevation float rasters.
# ---------------------------------------------------------------------------

# Import packages
import os
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import calculate_topographic_properties

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive, root_folder, 'Data/topography/Composite_10m/full')
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/full')
input_folder = os.path.join(data_folder, 'float')
output_folder = os.path.join(data_folder, 'integer')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

#### CREATE TOPOGRAPHY RASTERS

# Set initial count
count = 1

# Iterate through each buffered grid and calculate topography
for grid in grid_list:

    # Define folder structure
    output_path = os.path.join(output_folder, grid)

    # Define input datasets
    elevation_float = os.path.join(input_folder, grid, 'Elevation' + grid + '.tif')

    # Define output datasets
    elevation_integer = os.path.join(output_path, 'Elevation' + grid + '.tif')
    slope_integer = os.path.join(output_path, 'Slope_' + grid + '.tif')
    aspect_integer = os.path.join(output_path, 'Aspect_' + grid + '.tif')
    exposure_output = os.path.join(output_path, 'Exposure_' + grid + '.tif')
    heatload_output = os.path.join(output_path, 'HeatLoad_' + grid + '.tif')
    position_output = os.path.join(output_path, 'Position_' + grid + '.tif')
    radiation_output = os.path.join(output_path, 'Radiation_' + grid + '.tif')
    roughness_output = os.path.join(output_path, 'Roughness_' + grid + '.tif')
    surfacearea_output = os.path.join(output_path, 'SurfaceArea_' + grid + '.tif')
    surfacerelief_output = os.path.join(output_path, 'Relief_' + grid + '.tif')
    wetness_output = os.path.join(output_path, 'Wetness_' + grid + '.tif')

    # Make grid folder if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Define the grid raster
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # Create key word arguments
    kwargs_topography = {'z_unit': 'METER',
                         'position_width': 5000,
                         'input_array': [grid_raster, elevation_float],
                         'output_array': [elevation_integer,
                                          slope_integer,
                                          aspect_integer,
                                          exposure_output,
                                          heatload_output,
                                          position_output,
                                          radiation_output,
                                          roughness_output,
                                          surfacearea_output,
                                          surfacerelief_output,
                                          wetness_output]
                         }

    # Process the topographic calculations
    print(f'Processing topography for grid {count} of {len(grid_list)}...')
    arcpy_geoprocessing(calculate_topographic_properties, **kwargs_topography, check_output=False)
    print('----------')
