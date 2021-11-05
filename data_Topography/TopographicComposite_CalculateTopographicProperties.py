# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calculate topographic properties
# Author: Timm Nawrocki
# Last Updated: 2021-11-04
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
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
project_folder = os.path.join(drive, root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')
grid_folder = os.path.join(drive, root_folder, 'Data/analyses/grid_major/full')
input_folder = os.path.join(data_folder, 'float')
output_folder = os.path.join(data_folder, 'integer')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'BeringiaVegetation.gdb')

# Define grids
grid_list = ['A5', 'A6', 'A7', 'A8',
             'B4', 'B5', 'B6', 'B7', 'B8',
             'C4', 'C5', 'C6', 'C7', 'C8',
             'D4', 'D5', 'D6',
             'E4', 'E5', 'E6']

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

#### CREATE TOPOGRAPHY RASTERS

# Set initial count
count = 1

# Iterate through each buffered grid and calculate topography
for grid in grid_list:
    # Define folder structure
    output_path = os.path.join(output_folder, grid)
    input_raster = os.path.join(input_folder, grid, 'Elevation_AKALB_' + grid + '.tif')
    output_elevation = os.path.join(output_path, 'Elevation_AKALB_' + grid + '.tif')
    output_aspect = os.path.join(output_path, 'Aspect_AKALB_' + grid + '.tif')
    output_wetness = os.path.join(output_path, 'Wetness_AKALB_' + grid + '.tif')
    output_roughness = os.path.join(output_path, 'Roughness_AKALB_' + grid + '.tif')
    output_exposure = os.path.join(output_path, 'Exposure_AKALB_' + grid + '.tif')
    output_slope = os.path.join(output_path, 'Slope_AKALB_' + grid + '.tif')
    output_area = os.path.join(output_path, 'SurfaceArea_AKALB_' + grid + '.tif')
    output_relief = os.path.join(output_path, 'Relief_AKALB_' + grid + '.tif')
    output_position = os.path.join(output_path, 'Position_AKALB_' + grid + '.tif')
    output_radiation = os.path.join(output_path, 'Radiation_AKALB_' + grid + '.tif')
    output_heat = os.path.join(output_path, 'HeatLoad_AKALB_' + grid + '.tif')

    # Make grid folder if it does not already exist
    if os.path.exists(output_path) == 0:
        os.mkdir(output_path)

    # Define the grid raster
    grid_raster = os.path.join(grid_folder, grid + '.tif')

    # Create key word arguments
    kwargs_topography = {'z_unit': 'METER',
                         'input_array': [grid_raster, input_raster],
                         'output_array': [output_elevation,
                                          output_aspect,
                                          output_wetness,
                                          output_roughness,
                                          output_exposure,
                                          output_slope,
                                          output_area,
                                          output_relief,
                                          output_position,
                                          output_radiation]
                         }

    # Process the topographic calculations
    print(f'Processing topography for grid {count} of {len(grid_list)}...')
    arcpy_geoprocessing(calculate_topographic_properties, **kwargs_topography, check_output=False)
    print('----------')
