# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Analysis Grids
# Author: Timm Nawrocki
# Last Updated: 2019-11-05
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Analysis Grids" creates major and minor grid indices and overlapping grid tiles from a manually-generated study area polygon.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_buffered_tiles
from package_GeospatialProcessing import create_grid_indices
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/analyses')
project_folder = os.path.join(root_folder, 'Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(project_folder, 'BeringiaVegetation.gdb')

# Define input raster datasets
total_area = os.path.join(arcpy.env.workspace, 'northAmericanBeringia_TotalArea')
snap_raster = os.path.join(project_folder, 'Data_Input/northAmericanBeringia_TotalArea.tif')

# Define grid datasets
major_grid = os.path.join(arcpy.env.workspace, 'NorthAmericanBeringia_GridIndex_Major_400km')
minor_grid = os.path.join(arcpy.env.workspace, 'NorthAmericanBeringia_GridIndex_Minor_20km')

# Define input and output arrays
grid_inputs = [total_area]
grid_outputs = [major_grid, minor_grid]
major_inputs = [major_grid, snap_raster]
minor_inputs = [minor_grid, snap_raster]

# Create key word arguments
grid_kwargs = {'distance_major': '400 Kilometers',
               'distance_minor': '20 Kilometers',
               'input_array': grid_inputs,
               'output_array': grid_outputs
               }
major_kwargs = {'tile_name': 'Major',
                'distance': '10000 Meters',
                'input_array': major_inputs,
                'output_folder': os.path.join(data_folder, 'gridMajor'),
                'workspace': arcpy.env.workspace
                }
minor_kwargs = {'tile_name': 'Minor',
                'distance': '10 Meters',
                'input_array': minor_inputs,
                'output_folder': os.path.join(data_folder, 'gridMinor'),
                'workspace': arcpy.env.workspace
                }

# Create the major and minor grid indices
arcpy_geoprocessing(create_grid_indices, check_output = False, **grid_kwargs)

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output = False, **major_kwargs)

# Create buffered tiles for the minor grid
arcpy_geoprocessing(create_buffered_tiles, check_output = False, **minor_kwargs)
