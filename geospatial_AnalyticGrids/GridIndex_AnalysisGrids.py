# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create Analysis Grids
# Author: Timm Nawrocki
# Created on: 2019-10-27
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create Analysis Grids" creates major and minor overlapping grid tiles for feature development and analysis from manually generated grid indices based on the manually generated study area.
# ---------------------------------------------------------------------------

# Import packages
import arcpy
import os
from beringianGeospatialProcessing import arcpy_geoprocessing
from beringianGeospatialProcessing import create_buffered_tiles

# Set root directory
drive = 'K:/'
root_directory = os.path.join(drive, 'ACCS_Work/Projects/VegetationEcology/AKVEG_QuantitativeMap/Project_GIS')

# Set arcpy working environment
arcpy.env.workspace = os.path.join(root_directory, 'BeringiaVegetation.gdb')

# Define input datasets
major_grid = os.path.join(arcpy.env.workspace, 'NorthAmericanBeringia_GridIndex_Major_400km_Full')
minor_grid = os.path.join(arcpy.env.workspace, 'NorthAmericanBeringia_GridIndex_Minor_20km')
total_area = os.path.join(arcpy.env.workspace, 'NorthAmericanBeringia_TotalArea')

# Define input and output arrays
major_inputs = [major_grid, total_area]
minor_inputs = [minor_grid, total_area]

# Create key word arguments
major_kwargs = {'tile_name': 'PageName',
                'distance': '10000 Meters',
                'input_array': major_inputs,
                'output_geodatabase': os.path.join(root_directory, 'Analysis_GridMajor.gdb')
                }
minor_kwargs = {'tile_name': 'Name',
                'distance': '10 Meters',
                'input_array': minor_inputs,
                'output_geodatabase': os.path.join(root_directory, 'Analysis_GridMinor.gdb')
                }

# Process the create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output = False, **major_kwargs)

# Process the create buffered tiles for the minor grid
arcpy_geoprocessing(create_buffered_tiles, check_output = False, **minor_inputs)
