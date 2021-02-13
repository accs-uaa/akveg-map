# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Analysis Grids
# Author: Timm Nawrocki
# Last Updated: 2021-01-13
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Analysis Grids" creates major and minor grid indices and overlapping grid tiles from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_buffered_tiles
from package_GeospatialProcessing import create_grid_indices
from package_GeospatialProcessing import select_location
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/analyses')
project_folder = os.path.join(root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Data')

# Define work geodatabase
work_geodatabase = os.path.join(project_folder, 'BeringiaVegetation.gdb')

# Define input raster datasets
total_area = os.path.join(project_folder, 'Data_Input/northAmericanBeringia_TotalArea.tif')
study_area = os.path.join(project_folder, 'Data_Input/northAmericanBeringia_ModelArea.tif')
total_polygon = os.path.join(work_geodatabase, 'northAmericanBeringia_TotalArea')
study_polygon = os.path.join(work_geodatabase, 'NorthAmericanBeringia_ModelArea')

# Define output grid datasets
major_grid = os.path.join(work_geodatabase, 'NorthAmericanBeringia_GridIndex_Major_400km')
minor_grid = os.path.join(work_geodatabase, 'NorthAmericanBeringia_GridIndex_Minor_10km')
major_selected = os.path.join(work_geodatabase, 'NorthAmericanBeringia_GridIndex_Major_400km_Selected')
minor_selected = os.path.join(work_geodatabase, 'NorthAmericanBeringia_GridIndex_Minor_10km_Selected')

# Define input arrays
grid_inputs = [total_polygon]
select_major = [study_polygon, major_grid]
select_minor = [study_polygon, minor_grid]
major_inputs = [major_grid, total_area]
minor_inputs = [minor_selected, study_area]

# Define output arrays
grid_outputs = [major_grid, minor_grid]
major_output = [major_selected]
minor_output = [minor_selected]

# Create key word arguments
grid_kwargs = {'distance_major': '400 Kilometers',
               'distance_minor': '10 Kilometers',
               'work_geodatabase': work_geodatabase,
               'input_array': grid_inputs,
               'output_array': grid_outputs
               }
select_major_kwargs = {'work_geodatabase': work_geodatabase,
                       'input_array': select_major,
                       'output_array': major_output
                       }
select_minor_kwargs = {'work_geodatabase': work_geodatabase,
                       'input_array': select_minor,
                       'output_array': minor_output}
major_kwargs = {'tile_name': 'Major',
                'distance': '10000 Meters',
                'work_geodatabase': work_geodatabase,
                'input_array': major_inputs,
                'output_folder': os.path.join(data_folder, 'gridMajor')
                }
minor_kwargs = {'tile_name': 'Minor',
                'distance': '10 Meters',
                'work_geodatabase': work_geodatabase,
                'input_array': minor_inputs,
                'output_folder': os.path.join(data_folder, 'gridMinor')
                }

# Create the major and minor grid indices
print('Creating major and minor grid indices...')
arcpy_geoprocessing(create_grid_indices, check_output=False, **grid_kwargs)
print('----------')

# Select major grids
print('Selecting major grids within study area...')
arcpy_geoprocessing(select_location, check_output=False, **select_major_kwargs)
print('----------')

# Select minor grids
print('Selecting minor grids within study area...')
arcpy_geoprocessing(select_location, check_output=False, **select_minor_kwargs)
print('----------')

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **major_kwargs)
print('----------')

# Create buffered tiles for the minor grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **minor_kwargs)
print('----------')
