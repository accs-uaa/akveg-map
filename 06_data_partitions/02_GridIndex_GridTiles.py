# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Create grid tiles
# Author: Timm Nawrocki
# Last Updated: 2023-03-27
# Usage: Must be executed in an ArcGIS Pro Python 3.6 installation.
# Description: "Create grid tiles" creates overlapping grid tiles for analysis grids.
# ---------------------------------------------------------------------------

# Import packages
from package_GeospatialProcessing import arcpy_geoprocessing
from package_GeospatialProcessing import create_buffered_tiles
import os

# Set root directory
drive = 'N:/'
root_folder = os.path.join(drive, 'ACCS_Work')

# Set data folder
data_folder = os.path.join(root_folder, 'Data/analyses')
project_folder = os.path.join(root_folder, 'Projects/VegetationEcology/AKVEG_Map/Data')

# Define geodatabases
work_geodatabase = os.path.join(project_folder, 'AKVEG_Map.gdb')
regions_geodatabase = os.path.join(project_folder, 'Alaska_Regions.gdb')

# Define input raster datasets
total_feature = os.path.join(regions_geodatabase, 'AlaskaCombined_TotalArea')
total_raster = os.path.join(project_folder, 'Data_Input/AlaskaCombined_TotalArea.tif')
nab_feature = os.path.join(regions_geodatabase, 'NorthAmericanBeringia_ModelArea')
nab_raster = os.path.join(project_folder, 'Data_Input/NorthAmericanBeringia_ModelArea.tif')

#### CREATE GRID BLOCKS FOR MAJOR GRIDS

block_kwargs = {'tile_name': 'grid_major',
                'distance': '5000 Meters',
                'work_geodatabase': work_geodatabase,
                'input_array': [major_nab, total_raster],
                'output_folder': os.path.join(data_folder, 'grid_major/full')
                }

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **block_kwargs)
print('----------')

#### CREATE GRID BLOCKS FOR MAJOR GRIDS IN NORTH AMERICAN BERINGIA

block_nab_kwargs = {'tile_name': 'grid_major',
                    'distance': '5000 Meters',
                    'work_geodatabase': work_geodatabase,
                    'input_array': [major_nab, nab_raster],
                    'output_folder': os.path.join(data_folder, 'grid_major/nab')
                    }

# Create buffered tiles for the major grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **block_nab_kwargs)
print('----------')

#### CREATE GRID TILES FOR MINOR GRIDS IN NORTH AMERICAN BERINGIA

tile_nab_kwargs = {'tile_name': 'grid_minor',
                   'distance': '10 Meters',
                   'work_geodatabase': work_geodatabase,
                   'input_array': [minor_nab, nab_raster],
                   'output_folder': os.path.join(data_folder, 'grid_minor/nab')
                   }

# Create buffered tiles for the minor grid
arcpy_geoprocessing(create_buffered_tiles, check_output=False, **tile_nab_kwargs)
print('----------')